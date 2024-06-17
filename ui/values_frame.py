import tkinter as tk
from typing import Callable

from events import Events  # type: ignore[import-untyped]


class ValuesFrame(tk.Frame):
    _MARGIN = 20
    _CELL_SIDE = 60
    _CANV_WIDTH = _MARGIN * 2 + _CELL_SIDE
    _CANV_HEIGHT = _MARGIN * 2 + _CELL_SIDE * 9
    # tags
    _SELECTED = "selected"
    _REMAINING = "remaining"

    def __init__(self, master: tk.Misc):
        super().__init__(master)
        COLOR_BACKGROUND = "#fff"
        self._events = Events()
        self._canvas = tk.Canvas(self, width=self._CANV_WIDTH, height=self._CANV_HEIGHT, background=COLOR_BACKGROUND)
        self._canvas.pack(fill=tk.BOTH, side=tk.TOP)
        self._draw_grid()
        for i in range(1, 10):
            self._draw_value(i)
        self._canvas.bind("<Button-1>", lambda event: self._events.on_value_clicked(self._get_event_value(event)))

    def add_on_value_clicked_handler(self, handler: Callable[[int], None]) -> None:
        self._events.on_value_clicked += handler

    def draw_remaining_count(self, value: int, remaining: int) -> None:
        COLOR_VALUE = "#344861"
        coords = (
            self._MARGIN + self._CELL_SIDE - 10,
            self._MARGIN + (value - 1) * self._CELL_SIDE + self._CELL_SIDE - 10,
        )
        tags = [self._REMAINING, f"{self._REMAINING}{value}"]
        self._canvas.create_text(*coords, text=remaining, fill=COLOR_VALUE, font=("Helvetica", 10), tags=tags)

    def clear_remaining_counts(self, value: int | None = None) -> None:
        tag = f"{self._REMAINING}{value or ''}"
        self._canvas.delete(tag)

    def draw_selected_value(self, value: int) -> None:
        COLOR_CURSOR = "#c3d7ea"
        x0, y0 = self._MARGIN, self._MARGIN + (value - 1) * self._CELL_SIDE
        x1, y1 = self._MARGIN + self._CELL_SIDE, self._MARGIN + value * self._CELL_SIDE
        self._canvas.create_rectangle(x0, y0, x1, y1, fill=COLOR_CURSOR, tags=self._SELECTED)
        self._canvas.tag_lower(self._SELECTED)

    def clear_selected_value(self) -> None:
        self._canvas.delete(self._SELECTED)

    def _draw_grid(self) -> None:
        COLOR_BORDER = "#bfc6d4"
        x0, y0 = self._MARGIN, self._MARGIN
        x1, y1 = self._MARGIN + self._CELL_SIDE, self._CANV_HEIGHT - self._MARGIN
        self._canvas.create_rectangle(x0, y0, x1, y1, outline=COLOR_BORDER)
        x0, x1 = self._MARGIN, self._MARGIN + self._CELL_SIDE
        for i in range(1, 9):
            y = self._MARGIN + i * self._CELL_SIDE
            self._canvas.create_line(x0, y, x1, y, fill=COLOR_BORDER)

    def _draw_value(self, value: int) -> None:
        COLOR_VALUE = "#344861"
        coords = self._MARGIN + self._CELL_SIDE / 2, self._MARGIN + (value - 1) * self._CELL_SIDE + self._CELL_SIDE / 2
        self._canvas.create_text(*coords, text=value, fill=COLOR_VALUE, font=("Helvetica", 25))

    def _get_event_value(self, event: tk.Event) -> int:  # type: ignore[type-arg]
        if (
            self._MARGIN < event.x < self._CANV_WIDTH - self._MARGIN
            and self._MARGIN < event.y < self._CANV_HEIGHT - self._MARGIN
        ):
            return int((event.y - self._MARGIN) / self._CELL_SIDE) + 1
        return -1
