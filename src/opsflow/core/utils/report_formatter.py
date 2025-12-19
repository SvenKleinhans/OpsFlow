from typing import List

from ..models import Result, Severity


class ReportFormatter:
    """Formats workflow results into a report."""

    def __init__(self, results: List[Result]) -> None:
        """Initializes the Report Formatter with a list of results.

        Args:
            results (List[Result]): List of Result objects to format.
        """
        self.results = results

    def summary(self) -> str:
        """Creates a compact multi-line summary of results.

        Returns:
            str: A simple result summary grouped by severity.
        """
        if not self.results:
            return "No workflow results available."

        lines = ["Maintenance Summary", "====================", ""]

        for severity in sorted(Severity, key=lambda s: s.value, reverse=True):
            section = [r for r in self.results if r.severity == severity]
            if not section:
                continue

            lines.append(f"{severity.name}:")
            lines.append("-" * (len(severity.name) + 1))

            for r in section:
                lines.append(f"  Step:    {r.step}")
                lines.append(f"  Message: {r.message}")
                lines.append("")

        return "\n".join(lines)

    def format_report(self, logs: str = "") -> str:
        """Formats all results along with logs into a full report.

        Args:
            logs (str): Optional log string to append.

        Returns:
            str: Formatted workflow report with summary and logs.
        """
        report = self.summary()
        report += "\n\nLogs:\n-----\n"
        report += logs.strip() if logs else "(No logs available)"
        return report
