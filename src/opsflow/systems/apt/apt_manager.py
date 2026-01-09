import re
from opsflow.core.models import Result, Severity
from opsflow.core.system.system_manager import PackageManager
from opsflow.core.utils import CommandRunner


class AptManager(PackageManager):
    def upgrade(self, dry_run: bool = False) -> Result | None:
        result = self._run_apt(
            ["apt-get", "dist-upgrade", "-y"], "System Upgrade", dry_run
        )
        if result:
            return result
        return self._run_apt(
            ["apt-get", "autoremove", "-y"], "Remove Unused Packages", dry_run
        )

    def update(self, dry_run: bool = False) -> Result | None:
        if dry_run:
            return Result(
                step="System Update",
                severity=Severity.INFO,
                message="Dry-run: apt-get update skipped",
            )
        return CommandRunner.run_as_result(["apt-get", "update"], "System Update")

    def install(self, package: str, version: str | None) -> Result | None:
        if version:
            pkg = f"{package}={version}"
        else:
            pkg = package

        return self._run_apt(
            ["apt-get", "install", "-y", pkg],
            f"Install package {package}",
            dry_run=False,
        )

    def get_installed(self, package: str) -> str | None:
        result = CommandRunner.run(
            ["dpkg-query", "-W", "-f=${Status} ${Version}", package],
            env={"LC_ALL": "C"},
        )

        if result.returncode != 0:
            return None

        match = re.search(r"install ok installed ([^\s]+)", result.stdout)
        if not match:
            return None

        return match.group(1)

    def get_candidate(self, package: str) -> str | None:
        result = CommandRunner.run(
            ["apt-cache", "policy", package],
            env={"LC_ALL": "C"},
        )

        if result.returncode != 0:
            return None

        match = re.search(r"Candidate:\s*([^\s]+)", result.stdout)
        if not match:
            return None

        candidate = match.group(1)
        if candidate == "(none)":
            return None

        return candidate

    @staticmethod
    def _run_apt(args: list[str], step: str, dry_run: bool) -> Result | None:
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
