import pytest

from opsflow.plugins.gitlab import GitLabBackupConfig, GitLabConfig, GitLab
from opsflow.plugins.gitlab.gitlab_backup_service import GitLabBackupService


@pytest.fixture
def backup_config(tmp_path):
    backup_dir = tmp_path / "backups"
    gitlab_dir = tmp_path / "gitlab"

    backup_dir.mkdir(parents=True, exist_ok=True)
    gitlab_dir.mkdir(parents=True, exist_ok=True)

    return GitLabBackupConfig(
        backup_target_dir=backup_dir,
        gitlab_source_backup_dir=gitlab_dir,
    )


@pytest.fixture
def gitlab_config():
    return GitLabConfig()


@pytest.fixture
def plugin(gitlab_config, logger, context):
    return GitLab(gitlab_config, logger, context)


@pytest.fixture
def backuper(context, backup_config, logger):
    return GitLabBackupService(context, backup_config, logger)
