import logging


from opsflow.core.models import Result, Severity
from opsflow.plugins.gitlab.gitlab_backup_service import GitLabBackupService
from opsflow.plugins.gitlab import Hook


def test_run_backup_dry_run(context, backuper, caplog):
    context.dry_run = True

    with caplog.at_level(logging.INFO):
        assert backuper.run_backup() is True

    assert "Dry-run: would run gitlab-backup" in caplog.text
    assert context.all_results() == []


def test_run_backup_pre_hook_failure(context, backup_config, logger, monkeypatch):
    backup_config.pre_backup_hooks = [Hook(name="pre", cmd="false")]
    monkeypatch.setattr(
        "opsflow.plugins.gitlab.gitlab_backup_service.execute_hooks",
        lambda *_: False,
    )

    backuper = GitLabBackupService(context, backup_config, logger)

    assert backuper.run_backup() is False


def test_backup_repos_db_success(backuper, context):
    context.cmd.run_as_result = lambda *_: None

    assert backuper._backup_repositories_and_database() is True


def test_backup_repos_db_failure(backuper, context):
    context.cmd.run_as_result = lambda *_: Result(
        step="Backup",
        severity=Severity.ERROR,
        message="fail",
    )

    assert backuper._backup_repositories_and_database() is False
    assert len(context.all_results()) == 1


def test_copy_backup_no_files(backuper, context):
    assert backuper._copy_latest_repo_db_backup() is False

    results = context.all_results()
    assert len(results) == 1
    assert "No repository/database backup files found" in results[0].message


def test_copy_backup_success(backuper, backup_config):

    tar = backup_config.gitlab_source_backup_dir / "backup.tar"
    tar.write_text("data")

    assert backuper._copy_latest_repo_db_backup() is True


def test_backup_configuration_success(backuper, context):
    context.cmd.run_as_result = lambda *_: None

    assert backuper._backup_configuration() is True


def test_backup_configuration_failure(backuper, context):
    context.cmd.run_as_result = lambda *_: Result(
        step="Config Backup",
        severity=Severity.ERROR,
        message="fail",
    )

    assert backuper._backup_configuration() is False
    assert len(context.all_results()) == 1


def test_run_backup_unexpected_exception(backuper, context, monkeypatch):
    monkeypatch.setattr(
        backuper,
        "_backup_repositories_and_database",
        lambda: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    assert backuper.run_backup() is False

    results = context.all_results()
    assert len(results) == 1
    assert results[0].severity is Severity.ERROR
    assert "Unexpected backup error" in results[0].message
