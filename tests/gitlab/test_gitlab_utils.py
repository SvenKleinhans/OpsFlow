import logging
from opsflow.core.models import Result, Severity
from opsflow.plugins.gitlab.gitlab_backup_service import GitLabBackupService
from opsflow.plugins.gitlab import Hook
from opsflow.plugins.gitlab.utils import execute_hooks


def test_execute_hooks_no_hooks(context):
    assert execute_hooks(context, None) is True
    assert context.all_results() == []


def test_execute_hooks_success(context):
    hook = Hook(name="echo", cmd="echo ok")

    context.cmd.run_as_result = lambda *_, **__: None

    assert execute_hooks(context, [hook]) is True
    assert context.all_results() == []


def test_execute_hooks_failure_stops(context):
    hook = Hook(name="fail", cmd="false")

    context.cmd.run_as_result = lambda *_, **__: Result(
        step="fail",
        severity=Severity.ERROR,
        message="boom",
    )

    assert execute_hooks(context, [hook]) is False

    results = context.all_results()
    assert len(results) == 1
    assert results[0].severity is Severity.ERROR


def test_execute_hooks_continue_on_error(context):
    hooks = [
        Hook(name="fail", cmd="false", allow_failure=True),
        Hook(name="ok", cmd="echo ok"),
    ]

    def runner(cmd, name, env):
        if name == "fail":
            return Result(step=name, severity=Severity.ERROR, message="boom")
        return None

    context.cmd.run_as_result = runner

    assert execute_hooks(context, hooks) is True

    results = context.all_results()
    assert len(results) == 1


def test_execute_hooks_logs(context, logger, caplog):
    hook = Hook(name="echo", cmd="echo ok")
    context.cmd.run_as_result = lambda *_, **__: None

    with caplog.at_level(logging.INFO):
        execute_hooks(context, [hook], logger)

    assert "Running hook: echo → echo ok" in caplog.text


def test_backup_pre_hook_failure(context, backup_config, logger, monkeypatch):
    backup_config.pre_backup_hooks = [Hook(name="pre", cmd="false")]

    monkeypatch.setattr(
        "opsflow.plugins.gitlab.utils.execute_hooks",
        lambda *_: False,
    )

    backuper = GitLabBackupService(context, backup_config, logger)

    assert backuper.run_backup() is False
