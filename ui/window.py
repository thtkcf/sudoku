import tkinter as tk
from os import path
from tkinter import messagebox

from .grid_frame import GridFrame
from .side_panel_frame import SidePanelFrame
from .values_frame import ValuesFrame


class Window(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sudoku")
        file_path = path.join(path.dirname(__file__), "icons", "icon-76x76.png")
        icon = tk.PhotoImage(file=file_path)
        self.iconphoto(True, icon, icon)
        self.resizable(False, False)
        self._values_frame = ValuesFrame(self)
        self._values_frame.grid(row=0, column=0)
        self._grid_frame = GridFrame(self)
        self._grid_frame.grid(row=0, column=1)
        self._side_panel_frame = SidePanelFrame(self)
        self._side_panel_frame.grid(row=0, column=2, sticky=tk.N)

    @property
    def grid_frame(self) -> GridFrame:
        return self._grid_frame

    @property
    def values_frame(self) -> ValuesFrame:
        return self._values_frame

    @property
    def side_panel_frame(self) -> SidePanelFrame:
        return self._side_panel_frame

    def show_info(self, message: str) -> None:
        messagebox.showinfo(self.title(), message)
