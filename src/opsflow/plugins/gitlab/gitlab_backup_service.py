from datetime import datetime
import logging
import shutil

from opsflow.core.models import Result, Severity, Context
from .gitlab_config import GitLabBackupConfig
from .utils import execute_hooks


class GitLabBackupService:
    """Base class for performing GitLab backups.

    Handles repository & database backups, configuration backups, copying
    to a central backup directory, and optionally rotating old backups.
    """

    def __init__(
        self,
        ctx: Context,
        config: GitLabBackupConfig,
        logger: logging.Logger,
    ) -> None:
        """Initializes the GitLabBackupService.

        Args:
            ctx (Context): OpsFlow plugin context for command execution and result collection.
            config (GitLabBackuperConfig): Configuration object with backup parameters and paths.
            logger (logging.Logger): Logger instance to record backup steps and errors.
        """
        self.logger = logger
        self.config = config
        self.ctx = ctx

        # Create Backup directory
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.backup_dir = self.config.backup_target_dir / timestamp
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def run_backup(self) -> bool:
        """Performs a complete GitLab backup.

        Executes repository & database backup, copies the latest archive to
        the plugin backup directory, and runs configuration backup.

        Returns:
            bool: True if all steps completed successfully, False otherwise.
        """
        if self.ctx.dry_run:
            self.logger.info(
                "Dry-run: would run gitlab-backup and gitlab-ctl backup-etc"
            )
            return True

        try:
            env = {"OPSFLOW_GITLAB_BACKUP_DIR": str(self.backup_dir)}
            # Execute Pre-Hooks
            if not execute_hooks(
                self.ctx, self.config.pre_backup_hooks, self.logger, env=env
            ):
                return False

            if not self._backup_repositories_and_database():
                return False

            if not self._copy_latest_repo_db_backup():
                return False

            if not self._backup_configuration():
                return False

            # Execute Post-Hooks
            if not execute_hooks(
                self.ctx, self.config.post_backup_hooks, self.logger, env=env
            ):
                return False

            self.logger.info("Backup completed successfully")
            return True

        except Exception as e:
            self.logger.exception("Backup failed unexpectedly")
            self.ctx.add_result(
                Result(
                    step="Backup",
                    severity=Severity.ERROR,
                    message=f"Unexpected backup error: {e}",
                )
            )
            return False

    def _backup_repositories_and_database(self) -> bool:
        """Runs `gitlab-backup create` to back up repositories and the database.

        Returns:
            bool: True if the backup command succeeded, False otherwise.
        """
        self.logger.info("Running gitlab-backup (repositories and database)...")

        options = dict(self.config.gitlab_backup_options)
        options.setdefault("STRATEGY", "copy")

        cmd = ["gitlab-backup", "create"]

        for k, v in options.items():
            cmd.append(f"{k.upper()}={v}")

        result = self.ctx.cmd.run_as_result(cmd, "Backup GitLab Repos & DB")
        if result:
            self.ctx.add_result(result)
            return False
        return True

    def _copy_latest_repo_db_backup(self) -> bool:
        """Copies the latest repository/database backup to the central plugin backup directory.

        Returns:
            bool: True if copy succeeded, False otherwise.
        """
        print(self.config.gitlab_source_backup_dir)
        backup_files = list(self.config.gitlab_source_backup_dir.glob("*.tar"))
        print(backup_files)
        if not backup_files:
            msg = f"No repository/database backup files found in {self.config.gitlab_source_backup_dir}"
            self.logger.error(msg)
            self.ctx.add_result(
                Result(step="GitLab Backup", severity=Severity.ERROR, message=msg),
            )
            return False

        latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)
        try:
            shutil.copy(latest_backup, self.config.backup_target_dir)
            self.logger.info(
                "Copied latest repository/database backup %s to %s",
                latest_backup,
                self.config.backup_target_dir,
            )
            return True

        except Exception as e:
            msg = f"Failed to copy backup {latest_backup} to {self.config.backup_target_dir}: {e}"
            self.logger.exception(msg)
            self.ctx.add_result(
                Result(step="GitLab Backup", severity=Severity.ERROR, message=msg),
            )
            return False

    def _backup_configuration(self) -> bool:
        """Runs `gitlab-ctl backup-etc` to back up GitLab configuration.

        Returns:
            bool: True if the configuration backup succeeded, False otherwise.
        """
        self.logger.info("Running GitLab config backup...")
        result = self.ctx.cmd.run_as_result(
            [
                "gitlab-ctl",
                "backup-etc",
                "--backup-path",
                str(self.config.backup_target_dir),
            ],
            "GitLab Backup",
        )

        if result:
            self.logger.error("Backup of GitLab configuration failed")
            self.ctx.add_result(result)
            return False
        self.logger.info("GitLab config backup was successfull")
        return True
