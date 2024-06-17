import tkinter as tk
from tkinter import simpledialog
from tkinter.ttk import Separator
from typing import Callable

from events import Events  # type: ignore[import-untyped]


class SidePanelFrame(tk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self._events = Events()
        self._auto_cands = tk.BooleanVar()
        self._edit_cands = tk.BooleanVar()
        self._show_conflicts = tk.BooleanVar()
        import_field_button = tk.Button(self, text="Import Filed", command=self._on_import_field)
        import_field_button.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W + tk.E)
        init_cands_button = tk.Button(self, text="Init Candidates", command=self._events.on_init_candidates)
        init_cands_button.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W + tk.E)
        auto_cands_chb = tk.Checkbutton(self, text="Auto Candidates", variable=self._auto_cands)
        auto_cands_chb.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        edit_cands_chb = tk.Checkbutton(self, text="Edit Candidates", variable=self._edit_cands)
        edit_cands_chb.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        show_conflicts_chb = tk.Checkbutton(self, text="Highlight Conflicts", variable=self._show_conflicts)
        show_conflicts_chb.grid(row=3, column=0, columnspan=2, sticky=tk.W)
        self._undo_button = tk.Button(self, text="Undo", state=tk.DISABLED, command=self._events.on_undo)
        self._undo_button.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W + tk.E)
        self._redo_button = tk.Button(self, text="Redo", state=tk.DISABLED, command=self._events.on_redo)
        self._redo_button.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W + tk.E)
        reset_button = tk.Button(self, text="Reset", command=self._events.on_reset)
        reset_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W + tk.E)
        Separator(self, orient=tk.HORIZONTAL).grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W + tk.E)
        solve_step_button = tk.Button(self, text="Solve step", command=self._events.on_solve_step)
        solve_step_button.grid(row=7, column=0, padx=5, pady=5, sticky=tk.W + tk.E)
        solve_button = tk.Button(self, text="Solve", command=self._events.on_solve)
        solve_button.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W + tk.E)
        show_solution_button = tk.Button(self, text="Show solution", command=self._events.on_show_solution)
        show_solution_button.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W + tk.E)

    @property
    def auto_cands(self) -> bool:
        return self._auto_cands.get()

    @property
    def edit_cands(self) -> bool:
        return self._edit_cands.get()

    @property
    def show_conflicts(self) -> bool:
        return self._show_conflicts.get()

    @property
    def undo_state(self) -> bool:
        return self._undo_button["state"] != tk.DISABLED  # type: ignore[no-any-return]

    @undo_state.setter
    def undo_state(self, state: bool) -> None:
        self._undo_button.config(state=tk.NORMAL if state else tk.DISABLED)

    @property
    def redo_state(self) -> bool:
        return self._redo_button["state"] != tk.DISABLED  # type: ignore[no-any-return]

    @redo_state.setter
    def redo_state(self, state: bool) -> None:
        self._redo_button.config(state=tk.NORMAL if state else tk.DISABLED)

    def add_on_init_candidates_handler(self, handler: Callable[[], None]) -> None:
        self._events.on_init_candidates += handler

    def add_on_import_field_handler(self, handler: Callable[[str], None]) -> None:
        self._events.on_import_field += handler

    def add_on_undo_handler(self, handler: Callable[[], None]) -> None:
        self._events.on_undo += handler

    def add_on_redo_handler(self, handler: Callable[[], None]) -> None:
        self._events.on_redo += handler

    def add_on_reset_handler(self, handler: Callable[[], None]) -> None:
        self._events.on_reset += handler

    def add_on_solve_step_handler(self, handler: Callable[[], None]) -> None:
        self._events.on_solve_step += handler

    def add_on_solve_handler(self, handler: Callable[[], None]) -> None:
        self._events.on_solve += handler

    def add_on_show_solution_handler(self, handler: Callable[[], None]) -> None:
        self._events.on_show_solution += handler

    def _on_import_field(self) -> None:
        field = simpledialog.askstring(
            parent=self.master, title="Input Field", prompt="Enter 81 cells. Use 0 or . for empty cells"
        )
        if field:
            self._events.on_import_field(field)
