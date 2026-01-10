import pytest
from pathlib import Path
from opsflow.plugins.gitlab import GitLabConfig, GitLabEdition, GitLabBackupConfig


def test_package_name_ce():
    cfg = GitLabConfig(edition=GitLabEdition.CE)
    assert cfg.package_name == "gitlab-ce"


def test_backup_root_must_be_absolute():
    with pytest.raises(ValueError):
        GitLabBackupConfig(backup_target_dir=Path("relative/path"))
