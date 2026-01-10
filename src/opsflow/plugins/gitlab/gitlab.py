from packaging.version import Version, InvalidVersion
from opsflow.core.models import Result, Severity
from opsflow.core.plugin import Plugin

from .gitlab_backup_service import GitLabBackupService
from .gitlab_config import GitLabConfig
from .utils import execute_hooks


class GitLab(Plugin[GitLabConfig]):
    """Plugin to manage GitLab updates."""

    def run(self) -> None:
        # Standalone backup
        if self.config.run_backup and not self.config.run_update:
            self._backup()

        # Update flow
        elif self.config.run_update:
            if self.config.backup_before_update and not self._backup():
                # Abort if backup fails
                return
            self._update()

        else:
            self.logger.info("Neither update nor backup requested")

    def _validate_versions(self, installed: str | None, candidate: str | None) -> bool:
        """Validate installed and candidate versions, warn for major updates.

        Returns:
            bool: True if we can continue with update, False to abort.
        """
        if not installed:
            self._error("Could not determine installed GitLab version")
            return False
        if not candidate:
            self._error("Could not determine candidate GitLab version")
            return False
        if installed == candidate:
            self.logger.info("GitLab is already up to date")
            return False
        if self._is_major_update(installed, candidate):
            msg = f"Major GitLab update available ({installed} → {candidate}) – manual intervention required"
            self.logger.warning(msg)
            self.ctx.add_result(
                Result(step="GitLab Update", severity=Severity.WARNING, message=msg)
            )
            return False
        return True

    def _backup(self) -> bool:
        """Perform a backup using the installer.

        Returns:
            bool: True if succeeded, False otherwise.
        """
        self.logger.debug("Starting backup step...")
        backuper = GitLabBackupService(self.ctx, self.config.backup_config, self.logger)

        if not backuper.run_backup():
            self.logger.debug("GitLab backup failed")
            return False

        self.logger.debug("GitLab backup was successfull")
        return True

    def _update(self) -> bool:
        pkg_manager = self.ctx.pkg_manager
        if not pkg_manager:
            self._error("No package manager found")
            return False

        installed = pkg_manager.get_installed(self.config.package_name)
        candidate = pkg_manager.get_candidate(self.config.package_name)
        self.logger.debug(f"Installed GitLab version: {installed}")
        self.logger.debug(f"Candidate GitLab version: {candidate}")

        if not self._validate_versions(installed, candidate):
            return False

        # Execute Pre-Hooks
        if not execute_hooks(self.ctx, self.config.pre_update_hooks, self.logger):
            return False

        result = pkg_manager.install(self.config.package_name, candidate)
        if result:
            self.ctx.add_result(result)
            return False

        # Execute Post-Hooks
        if not execute_hooks(self.ctx, self.config.post_update_hooks, self.logger):
            return False

        if self.config.auto_restart and not self._restart():
            return False

        return True

    def _restart(self) -> bool:
        """Restart GitLab if auto_restart is enabled.

        Returns:
            bool: True if succeeded, False otherwise.
        """
        result = self.ctx.cmd.run_as_result(["gitlab-ctl", "restart"], "Restart GitLab")
        if result:
            self._error("GitLab restart failed")
            return False
        return True

    def _is_major_update(self, installed: str, candidate: str) -> bool:
        """Determine if the update is a major version change.

        Args:
            installed (str): Currently installed GitLab version.
            candidate (str): Candidate GitLab version available for update.

        Returns:
            bool: True if the major version differs, False otherwise.
        """
        try:
            return Version(installed).major != Version(candidate).major
        except InvalidVersion:
            self.logger.exception("Failed to check GitLab Versions")
            return False

    def _error(self, message: str) -> None:
        """Log an error and add it to the plugin results.

        Args:
            message (str): Error message to log and report.
        """
        self.logger.error(message)
        self.ctx.add_result(
            Result(
                step="GitLab Update",
                severity=Severity.ERROR,
                message=message,
            )
        )
