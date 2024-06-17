from typing import Iterable

from solver import BruteForcer, Solver, SolverException
from sudoku import Cell, Grid, SudokuException

from .grid_frame import Cursor
from .window import Window


class Controller:
    def __init__(self, window: Window, grid: Grid):
        self._window = window
        self._grid = grid
        self._grid.history_manager.enable_history()
        self._grid.history_manager.add_on_change_handler(self._on_grid_changed)
        self._brute_forcer = BruteForcer(self._grid)
        self._cell: Cell | None = None
        self._value: int | None = None
        self._update_value_counts()

    def bind(self) -> None:
        self._window.values_frame.add_on_value_clicked_handler(self._on_value_clicked)
        self._window.grid_frame.add_on_cell_clicked_handler(self._on_cell_clicked)
        self._window.grid_frame.add_on_key_pressed_handler(self._on_key_pressed)
        self._window.side_panel_frame.add_on_init_candidates_handler(lambda: self._grid.init_candidates())
        self._window.side_panel_frame.add_on_undo_handler(self._on_undo)
        self._window.side_panel_frame.add_on_redo_handler(self._on_redo)
        self._window.side_panel_frame.add_on_reset_handler(self._on_reset)
        self._window.side_panel_frame.add_on_import_field_handler(self._on_import_field)
        self._window.side_panel_frame.add_on_solve_step_handler(self._on_solve_step)
        self._window.side_panel_frame.add_on_solve_handler(self._on_solve)
        self._window.side_panel_frame.add_on_show_solution_handler(self._on_show_solution)

    def _on_cell_clicked(self, cell: tuple[int, int]) -> None:
        cell_new = self._grid.get_cell(*cell) if cell != (-1, -1) else None
        self._cell = cell_new if self._cell != cell_new else None
        if self._cell and not self._cell.is_given:
            self._window.grid_frame.set_focus(True)
        else:
            self._window.grid_frame.set_focus(False)
        self._update_grid_cursors()

    def _on_key_pressed(self, keysym: str) -> None:
        if not self._cell:
            return
        if keysym in ("Down", "Up", "Left", "Right"):
            self._change_selected_cell(keysym)
            self._update_grid_cursors()
            return
        if not keysym.isdigit():
            return
        if self._window.side_panel_frame.edit_cands:
            self._change_cell_candidates(int(keysym))
        else:
            self._change_cell_value(int(keysym))

    def _on_value_clicked(self, value: int) -> None:
        self._value = value if value not in (-1, self._value) else None
        self._update_selected_value()
        self._update_grid_cursors()

    def _on_import_field(self, field: str) -> None:
        try:
            grid = Grid(field)
        except SudokuException as e:
            self._window.show_info(str(e))
            return
        self._grid.history_manager.remove_on_change_handler(self._on_grid_changed)
        self._grid = grid
        self._grid.history_manager.enable_history()
        self._grid.history_manager.add_on_change_handler(self._on_grid_changed)
        self._brute_forcer = BruteForcer(self._grid)
        self._cell = None
        self._value = None
        self._update_selected_value()
        self._update_value_counts()
        self._update_undo_redo_state()
        self._update_grid()
        self._update_grid_cursors()

    def _on_solve_step(self) -> None:
        try:
            if not Solver(self._grid).solve_step():
                self._window.show_info("No step progress")
        except SolverException as e:
            self._window.show_info(str(e))

    def _on_solve(self) -> None:
        try:
            if not Solver(self._grid).solve():
                self._window.show_info("Not solved")
        except SolverException as e:
            self._window.show_info(str(e))

    def _on_show_solution(self) -> None:
        solution = self._brute_forcer.create_solution()
        if not solution:
            self._window.show_info("No solution not found")
        elif solution != "".join(str(cell.value) for cell in self._grid.cells):
            self._apply_solution(solution)
        else:
            self._window.show_info("Same solution achieved")

    def _on_undo(self) -> None:
        self._brute_forcer.reset()
        self._grid.history_manager.undo()

    def _on_redo(self) -> None:
        self._brute_forcer.reset()
        self._grid.history_manager.redo()

    def _on_reset(self) -> None:
        self._brute_forcer.reset()
        self._grid.reset()

    def _on_grid_changed(self) -> None:
        self._update_grid()
        self._update_grid_cursors()
        self._update_value_counts()
        self._update_undo_redo_state()
        if self._grid.is_solved and self._grid.is_consistent:
            self._window.show_info("Solved!")

    def _change_selected_cell(self, keysym: str) -> None:
        if not self._cell:
            return
        col, row = self._cell.coordinates
        match keysym:
            case "Right":
                col = col + 1 if col < 8 else 0
            case "Left":
                col = col - 1 if col > 0 else 8
            case "Down":
                row = row + 1 if row < 8 else 0
            case "Up":
                row = row - 1 if row > 0 else 8
        self._cell = self._grid.get_cell(col, row)

    def _change_cell_candidates(self, value: int) -> None:
        if not self._cell or not value:
            return
        if value in self._cell.candidates:
            self._cell.candidates -= {value}
        else:
            self._cell.candidates |= {value}

    def _change_cell_value(self, value: int) -> None:
        if not self._cell:
            return
        value = value if value != self._cell.value else 0
        if self._window.side_panel_frame.auto_cands:
            self._grid.set_value(self._cell, value)
        else:
            self._cell.value = value

    def _apply_solution(self, solution: Iterable[str]) -> None:
        if not self._grid.history_manager.is_complex_action:
            return self._grid.history_manager.as_complex_action(self._apply_solution, solution)
        for cell, value in zip(self._grid.cells, solution):
            cell.value = int(value)

    def _update_selected_value(self) -> None:
        self._window.values_frame.clear_selected_value()
        if self._value is not None:
            self._window.values_frame.draw_selected_value(self._value)

    def _update_value_counts(self) -> None:
        values = tuple(cell.value for cell in self._grid.filter_cells(solved=True))
        for i in range(1, 10):
            count = 9 - values.count(i)
            self._window.values_frame.clear_remaining_counts(i)
            self._window.values_frame.draw_remaining_count(i, count)

    def _update_grid(self) -> None:
        self._window.grid_frame.clear_values()
        self._window.grid_frame.clear_candidates()
        for cell in self._grid.cells:
            if cell.value:
                self._window.grid_frame.draw_value(cell.coordinates, cell.value, cell.is_given)
            self._window.grid_frame.draw_candidates(cell.coordinates, cell.candidates)

    def _update_grid_cursors(self) -> None:
        self._window.grid_frame.clear_cursors()
        if self._value is not None:
            self._draw_same_val_cursors(self._value)
            self._draw_has_cand_cursors(self._value)
            self._draw_selected_cursor()
        elif self._cell:
            self._draw_neighbor_cursors()
            self._draw_same_val_cursors(self._cell.value)
            self._draw_conflict_cursors()
            self._draw_has_cand_cursors(self._cell.value)
            self._draw_selected_cursor()

    def _update_undo_redo_state(self) -> None:
        self._window.side_panel_frame.undo_state = self._grid.history_manager.is_undo_possible
        self._window.side_panel_frame.redo_state = self._grid.history_manager.is_redo_possible

    def _draw_selected_cursor(self) -> None:
        if not self._cell:
            return
        self._window.grid_frame.draw_cursor(self._cell.coordinates, Cursor.SELECTED)

    def _draw_same_val_cursors(self, value: int) -> None:
        if not value:
            return
        for cell in self._grid.filter_cells(value=value):
            self._window.grid_frame.draw_cursor(cell.coordinates, Cursor.SAME_VAL)

    def _draw_has_cand_cursors(self, candidate: int) -> None:
        if not candidate:
            return
        for cell in self._grid.filter_cells(has_candidate=candidate):
            self._window.grid_frame.draw_cursor(cell.coordinates, Cursor.HAS_CAND)

    def _draw_neighbor_cursors(self) -> None:
        if not self._cell:
            return
        for cell in self._grid.get_neighbors(self._cell):
            self._window.grid_frame.draw_cursor(cell.coordinates, Cursor.NEIGHBOR)

    def _draw_conflict_cursors(self) -> None:
        if not self._cell or not self._cell.is_solved or not self._window.side_panel_frame.show_conflicts:
            return
        for cell in self._grid.get_neighbors(self._cell, value=self._cell.value):
            self._window.grid_frame.draw_cursor(cell.coordinates, Cursor.CONFLICT)
