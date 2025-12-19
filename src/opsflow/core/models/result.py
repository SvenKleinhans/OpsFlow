from dataclasses import dataclass
from enum import Enum
import threading
from typing import List, Optional


class Severity(Enum):
    """Enumeration of severity levels for workflow results."""

    INFO = 1
    WARNING = 2
    ERROR = 3


@dataclass
class Result:
    """Represents the result of a single workflow step.

    Args:
        step (str): Name or description of the step.
        severity (Severity): Severity level of the result.
        message (str): Human-readable message for the result.
    """

    step: str
    severity: Severity
    message: str


class ResultCollector:
    """Collects and formats workflow results.

    Supports adding results, computing an aggregate severity,
    and producing summaries for notifications or logs.
    """

    def __init__(self):
        """Initializes an empty ResultCollector."""
        self.results: List[Result] = []
        self._lock = threading.Lock()

    def add(self, result: Optional[Result]) -> None:
        """Adds a result to the collection.

        Args:
            result (Optional[Result]): Result object to add. None is ignored.
        """
        if result:
            with self._lock:
                self.results.append(result)

    def add_all(self, results: List[Result]) -> None:
        """Adds multiple results to the collection.

        Args:
            results (List[Result]): List of Result objects to add.
        """
        with self._lock:
            self.results.extend(results)

    def all_results(self) -> List[Result]:
        """
        Retrieves all collected results.

        Returns:
            List[Result]: A list of all collected results.
        """
        with self._lock:
            return list(self.results)

    def overall_severity(self) -> Severity:
        """Determines the highest severity among all results.

        Returns:
            Severity: The highest severity (INFO if no results exist).
        """
        if not self.results:
            return Severity.INFO
        return max((r.severity for r in self.results), key=lambda s: s.value)
