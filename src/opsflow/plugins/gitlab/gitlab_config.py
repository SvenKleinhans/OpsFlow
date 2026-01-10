from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from opsflow.core.config import PluginConfig


class GitLabEdition(str, Enum):
    """Supported GitLab editions."""

    EE = "ee"
    CE = "ce"


class Hook(BaseModel):
    """Represents a shell command hook executed during a workflow step.

    Attributes:
        name (str): Human-readable name of the hook.
        cmd (str): Shell command to execute.
        allow_failure (bool): Whether execution may continue if the hook fails.
    """

    name: str
    cmd: str
    allow_failure: bool = False


class GitLabBackupConfig(BaseModel):
    """Configuration for GitLab backup execution.

    This configuration controls where GitLab writes its internal backups,
    where OpsFlow stores the final backup artifacts, and which hooks are
    executed before and after the backup process.
    """

    backup_target_dir: Path = Field(
        default=Path("/var/opsflow/backups/gitlab"),
        description="Directory where final backup artifacts are stored.",
    )

    gitlab_source_backup_dir: Path = Field(
        default=Path("/var/opt/gitlab/backups"),
        description="Directory where GitLab writes repository and database backups.",
    )

    gitlab_backup_options: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional options passed to `gitlab-backup create`.",
    )

    pre_backup_hooks: Optional[List[Hook]] = None
    post_backup_hooks: Optional[List[Hook]] = None

    @field_validator("backup_target_dir", "gitlab_source_backup_dir")
    def validate_absolute_path(cls, value: Path) -> Path:
        """Ensure configured paths are absolute.

        Args:
            value (Path): Path to validate.

        Returns:
            Path: Resolved absolute path.

        Raises:
            ValueError: If the path is not absolute.
        """
        if not value.is_absolute():
            raise ValueError("Path must be absolute")
        return value.resolve()


class GitLabConfig(PluginConfig):
    """Top-level configuration for the GitLab OpsFlow plugin.

    Controls whether backups and/or updates are executed, as well as
    update behavior and sub-configurations.
    """

    edition: GitLabEdition = GitLabEdition.EE

    # Execution control
    run_update: bool = True
    run_backup: bool = False
    backup_before_update: bool = True

    # Update behavior
    auto_restart: bool = True

    # Sub-configurations
    backup_config: GitLabBackupConfig = GitLabBackupConfig()
    pre_update_hooks: Optional[List[Hook]] = None
    post_update_hooks: Optional[List[Hook]] = None

    @property
    def package_name(self) -> str:
        """Returns the GitLab package name based on the edition.

        Returns:
            str: Package name in the format ``gitlab-ee`` or ``gitlab-ce``.
        """
        return f"gitlab-{self.edition.value}"
