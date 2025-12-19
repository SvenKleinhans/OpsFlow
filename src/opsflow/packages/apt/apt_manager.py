from typing import Optional

from opsflow.core.system.base import PackageManager
from opsflow.core.models import Result
from opsflow.core.utils import CommandRunner


class AptManager(PackageManager):
    def upgrade(self, dry_run: bool = False) -> Optional[Result]:
        result = self._run_apt(
            ["apt-get", "dist-upgrade", "-y"], "System Upgrade", dry_run
        )
        if result:
            return result
        return self._run_apt(
            ["apt-get", "autoremove", "-y"], "Remove Unused Packages", dry_run
        )

    def update(self, dry_run: bool = False) -> Optional[Result]:
        return CommandRunner.run_as_result(["apt-get", "update"], "System Update")

    @staticmethod
    def _run_apt(args: list[str], step: str, dry_run: bool) -> Optional[Result]:
        """Run an apt command and return the result.

        Optionally executes the command in simulation mode when `dry_run`
        is enabled.

        Args:
            args (list[str]): Command-line arguments for apt.
            step (str): Context step name used for result reporting.
            dry_run (bool): If True, run apt in simulation mode.

        Returns:
            Optional[Result]: The command result, or None if execution failed.
        """
        if dry_run:
            args.insert(1, "--simulate")
        return CommandRunner.run_as_result(args, step)
