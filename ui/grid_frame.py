import tkinter as tk
from enum import Enum
from typing import Callable, Iterable

from events import Events  # type: ignore[import-untyped]


class Cursor(Enum):
    SELECTED = "#bbdefb"
    NEIGHBOR = "#e2ebf3"
    SAME_VAL = "#c3d7ea"
    CONFLICT = "#f7cfd6"
    HAS_CAND = "#d4ebda"


class GridFrame(tk.Frame):
    _MARGIN = 20
    _CELL_SIDE = 60
    _GRID_SIDE = 2 * _MARGIN + 9 * _CELL_SIDE
    # tags
    _CURSOR = "cursor"
    _CANDIDATE = "candidate"
    _VALUE = "value"

    def __init__(self, master: tk.Misc):
        super().__init__(master)
        COLOR_BACKGROUND = "#fff"
        self._events = Events()
        self._grid_canvas = tk.Canvas(self, width=self._GRID_SIDE, height=self._GRID_SIDE, background=COLOR_BACKGROUND)
        self._grid_canvas.pack(fill=tk.BOTH, side=tk.TOP)
        self._draw_grid()
        self._grid_canvas.bind("<Button-1>", lambda event: self._events.on_cell_clicked(self._get_event_cell(event)))
        self._grid_canvas.bind("<Key>", lambda event: self._events.on_key_pressed(event.keysym))

    def __str__(self) -> str:
        return "GridFrame"

    def add_on_cell_clicked_handler(self, handler: Callable[[tuple[int, int]], None]) -> None:
        self._events.on_cell_clicked += handler

    def add_on_key_pressed_handler(self, handler: Callable[[str], None]) -> None:
        self._events.on_key_pressed += handler

    def set_focus(self, focus: bool) -> None:
        if focus:
            self._grid_canvas.focus_set()
        else:
            self.focus_set()

    def draw_value(self, cell: tuple[int, int], value: int, is_given: bool) -> None:
        COLOR_GIVEN = "#344861"
        COLOR_SOLUTION = "#325aaf"
        tags = [self._VALUE, f"{self._VALUE}{cell}"]
        fill = COLOR_GIVEN if is_given else COLOR_SOLUTION
        coords = self._get_value_coordinates(cell)
        self._grid_canvas.create_text(*coords, text=value, tags=tags, fill=fill, font=("Helvetica", 25))

    def clear_values(self, cell: tuple[int, int] | None = None) -> None:
        tag = f"{self._VALUE}{cell or ''}"
        self._grid_canvas.delete(tag)

    def draw_candidates(self, cell: tuple[int, int], candidates: Iterable[int]) -> None:
        COLOR_NOTES = "#6e7c8c"
        tags = [self._CANDIDATE, f"{self._CANDIDATE}{cell}"]
        for cand in candidates:
            coords = self._get_candidate_coordinates(cell, cand)
            self._grid_canvas.create_text(*coords, text=cand, tags=tags, fill=COLOR_NOTES, font=("Helvetica", 10))

    def clear_candidates(self, cell: tuple[int, int] | None = None) -> None:
        tag = f"{self._CANDIDATE}{cell or ''}"
        self._grid_canvas.delete(tag)

    def draw_cursor(self, cell: tuple[int, int], cursor: Cursor) -> None:
        rectangle = self._get_cell_rectangle(cell)
        tags = [self._CURSOR, f"{self._CURSOR}{cursor.name}"]
        self._grid_canvas.create_rectangle(*rectangle, fill=cursor.value, tags=tags)
        self._grid_canvas.tag_lower(self._CURSOR)

    def clear_cursors(self, cursor: Cursor | None = None) -> None:
        tag = f"{self._CURSOR}{cursor.name if cursor else ''}"
        self._grid_canvas.delete(tag)

    def _get_cell_coordibnates(self, cell: tuple[int, int]) -> tuple[int, int]:
        return self._MARGIN + cell[0] * self._CELL_SIDE, self._MARGIN + cell[1] * self._CELL_SIDE

    def _get_cell_rectangle(self, cell: tuple[int, int]) -> tuple[int, int, int, int]:
        x0, y0 = self._get_cell_coordibnates(cell)
        x1, y1 = x0 + self._CELL_SIDE, y0 + self._CELL_SIDE
        return x0, y0, x1, y1

    def _get_value_coordinates(self, cell: tuple[int, int]) -> tuple[float, float]:
        cell_coords = self._get_cell_coordibnates(cell)
        x_offset = y_offset = self._CELL_SIDE / 2
        return cell_coords[0] + x_offset, cell_coords[1] + y_offset

    def _get_candidate_coordinates(self, cell: tuple[int, int], candidate: int) -> tuple[float, float]:
        cell_coords = self._get_cell_coordibnates(cell)
        cand_idx = candidate - 1
        x_offset = self._CELL_SIDE / 3 * (cand_idx % 3) + 10
        y_offset = self._CELL_SIDE / 3 * (cand_idx // 3) + 10
        return cell_coords[0] + x_offset, cell_coords[1] + y_offset

    def _draw_grid(self) -> None:
        COLOR_CELL_BORDER = "#bfc6d4"
        COLOR_BOX_BORDER = "#344861"
        COLOR_COORDINATES = "#325aaf"
        for i in range(10):
            # coordinates
            coords = self._MARGIN + i * self._CELL_SIDE + self._CELL_SIDE / 2, self._MARGIN / 2
            self._grid_canvas.create_text(*coords, text=i, fill=COLOR_COORDINATES, font=("Helvetica", 8))
            self._grid_canvas.create_text(*reversed(coords), text=i, fill=COLOR_COORDINATES, font=("Helvetica", 8))
            # can skip because it will be covered by outer and box borders
            if not i % 3:
                continue
            # cells border
            x0, y0 = self._MARGIN + i * self._CELL_SIDE, self._MARGIN
            x1, y1 = self._MARGIN + i * self._CELL_SIDE, self._GRID_SIDE - self._MARGIN
            self._grid_canvas.create_line(x0, y0, x1, y1, fill=COLOR_CELL_BORDER)
            # invers both points coordinates to draw vertical line
            self._grid_canvas.create_line(y0, x0, y1, x1, fill=COLOR_CELL_BORDER)
        # box border
        for i in (3, 6):
            x0, y0 = self._MARGIN, self._MARGIN + i * self._CELL_SIDE
            x1, y1 = self._GRID_SIDE - self._MARGIN, self._MARGIN + i * self._CELL_SIDE
            self._grid_canvas.create_line(x0, y0, x1, y1, fill=COLOR_BOX_BORDER, width=2)
            # invers both points coordinates to draw vertical line
            self._grid_canvas.create_line(y0, x0, y1, x1, fill=COLOR_BOX_BORDER, width=2)
        # outer border
        x0, y0 = self._MARGIN, self._MARGIN
        x1, y1 = self._GRID_SIDE - self._MARGIN, self._GRID_SIDE - self._MARGIN
        self._grid_canvas.create_rectangle(x0, y0, x1, y1, outline=COLOR_BOX_BORDER, width=2)

    def _get_event_cell(self, event: tk.Event) -> tuple[int, int]:  # type: ignore[type-arg]
        if (
            self._MARGIN < event.x < self._GRID_SIDE - self._MARGIN
            and self._MARGIN < event.y < self._GRID_SIDE - self._MARGIN
        ):
            return int((event.x - self._MARGIN) / self._CELL_SIDE), int((event.y - self._MARGIN) / self._CELL_SIDE)
        return -1, -1
