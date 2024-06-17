from sudoku import Grid

from .controller import Controller
from .window import Window


class App:
    def __init__(self) -> None:
        self._window = Window()
        grid = Grid("0" * 81)
        self._controller = Controller(self._window, grid)
        self._controller.bind()

    def start(self) -> None:
        self._window.mainloop()
