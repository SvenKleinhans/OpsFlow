from ..utils.command_runner import CommandRunner
from .result import Result, ResultCollector


class Context:
    """Shared context provided to all components.

    Contains only lightweight, globally relevant services.
    """

    def __init__(self, result_collector: ResultCollector, dry_run: bool):
        self._result_collector = result_collector
        self.dry_run = dry_run
        self.cmd = CommandRunner

    def add_result(self, result: Result | None) -> None:
        """
        Adds a result to the context's result collector.

        Args:
            result (Optional[Result]): The result to add.
        """
        self._result_collector.add(result)

    def add_results(self, results: list[Result]) -> None:
        """
        Adds multiple results to the context's result collector.

        Args:
            results (List[Result]): The list of results to add.
        """
        self._result_collector.add_all(results)

    def all_results(self) -> list[Result]:
        """
        Retrieves all results from the context's result collector.

        Returns:
            List[Result]: List of all collected results.
        """
        return self._result_collector.all_results()
