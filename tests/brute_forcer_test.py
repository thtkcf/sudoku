import unittest
from logging import WARNING
from os import path

from solver import BruteForcer
from sudoku import Grid


class BruteForcerTest(unittest.TestCase):
    def test_solutions(self) -> None:
        self._test_solutions("topn87_hr.txt")

    def test_multiple_solutions(self) -> None:
        file_path = path.join(path.dirname(__file__), "datasets", "multiple_solutions.txt")
        with open(file_path) as file:
            for line in file:
                quiz, *solutions = line.strip().split(",")
                brute_forcer = BruteForcer(Grid(quiz))
                results: list[str] = []
                for _ in range(len(solutions)):
                    with self.assertNoLogs(level=WARNING):
                        result = brute_forcer.create_solution()
                    self.assertIsNotNone(result, f"{quiz} not all solutions found")
                    results.append(result)  # type: ignore[arg-type]
                with self.assertLogs(level=WARNING):
                    self.assertIsNone(brute_forcer.create_solution(), f"{quiz} too much solutions found")
                self.assertEqual(sorted(results), sorted(solutions), f"{quiz} wrong solutions")

    def test_no_solutions(self) -> None:
        file_path = path.join(path.dirname(__file__), "datasets", "no_solutions.txt")
        num_of_attempts = 5
        with open(file_path) as file:
            for line in file:
                quiz = line.strip()
                brute_forcer = BruteForcer(Grid(quiz))
                for _ in range(num_of_attempts):
                    with self.assertLogs(level=WARNING):
                        self.assertIsNone(brute_forcer.create_solution(), f"{quiz} should be unsolvable")

    def _test_solutions(self, file_name: str) -> None:
        file_path = path.join(path.dirname(__file__), "datasets", file_name)
        with open(file_path) as file:
            for line in file:
                quiz, solution = line.strip().split(",")
                brute_forcer = BruteForcer(Grid(quiz))
                with self.assertNoLogs(level=WARNING):
                    self.assertEqual(brute_forcer.create_solution(), solution, f"{quiz}: wrong solution")
                self.assertIsNone(brute_forcer.create_solution(), f"{quiz} multiple solutions found")


if __name__ == "__main__":
    unittest.main()
