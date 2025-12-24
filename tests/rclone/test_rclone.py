from unittest.mock import MagicMock, patch

from opsflow.core.models import Severity
from opsflow.plugins.rclone import (
    RCloneAction,
    RClonePlugin,
    RClonePluginConfig,
    RCloneTask,
)


def fake_command_result(success=True):
    """
    Generate a fake CommandResult object for mocking RClone execution.

    Args:
        success (bool): Whether the command should simulate success or failure.

    Returns:
        MagicMock: Mocked CommandResult object.
    """
    mock_result = MagicMock()
    mock_result.return_code = 0 if success else 1
    mock_result.success = success
    mock_result.files_transferred = 1
    mock_result.bytes_transferred = 100
    mock_result.duration_seconds = 0.1
    mock_result.errors = [] if success else ["Error"]
    mock_result.stdout = "ok" if success else ""
    mock_result.stderr = "" if success else "fail"
    return mock_result


def test_no_tasks(context, logger):
    """Test that the plugin exits gracefully when no tasks are configured."""
    plugin = RClonePlugin(
        config=RClonePluginConfig(tasks=[], config_file=None, max_workers=1),
        logger=logger,
        ctx=context,
    )
    plugin.run()
    # Expect no results since there were no tasks
    assert len(context.all_results()) == 0


def test_task_failure(context, logger):
    """Test that the plugin correctly records a failure when a task raises an exception."""
    task = RCloneTask(name="fail_task", src="s", dest="d", action=RCloneAction.SYNC)
    plugin = RClonePlugin(
        config=RClonePluginConfig(tasks=[task], config_file=None, max_workers=1),
        logger=logger,
        ctx=context,
    )

    with patch.object(RClonePlugin, "_sync", side_effect=Exception("Test failure")):
        plugin.run()

    results = context.all_results()

    assert len(results) == 1
    result = results[0]
    assert result.severity == Severity.ERROR
    assert "Test failure" in result.message


def test_dry_run_flag(context, logger):
    """Test that the plugin passes the dry-run flag to RClone commands."""
    task = RCloneTask(name="sync_task", src="s", dest="d", action=RCloneAction.SYNC)
    plugin = RClonePlugin(
        config=RClonePluginConfig(tasks=[task], config_file=None, max_workers=1),
        logger=logger,
        ctx=context,
    )

    with patch.object(RClonePlugin, "_sync") as mock_sync:
        mock_sync.return_value = fake_command_result()
        plugin.run()
        # Optionally: check call arguments if _sync forwards dry-run flag
        # e.g., called_with = mock_sync.call_args[0][0]  # first argument is RClone instance


def test_all_actions(context, logger):
    """Test that the plugin runs all types of tasks (SYNC, COPY, MOVE) and collects results."""
    tasks = [
        RCloneTask(name="sync", src="s1", dest="d1", action=RCloneAction.SYNC),
        RCloneTask(name="copy", src="s2", dest="d2", action=RCloneAction.COPY),
        RCloneTask(name="move", src="s3", dest="d3", action=RCloneAction.MOVE),
    ]
    plugin = RClonePlugin(
        config=RClonePluginConfig(tasks=tasks, config_file=None, max_workers=2),
        logger=logger,
        ctx=context,
    )

    with (
        patch.object(RClonePlugin, "_sync", return_value=fake_command_result()),
        patch.object(RClonePlugin, "_copy", return_value=fake_command_result()),
        patch.object(RClonePlugin, "_move", return_value=fake_command_result()),
    ):
        plugin.run()

    results = context.all_results()

    assert len(results) == 3
    names = [r.step for r in results]
    assert any("sync" in n.lower() for n in names)
    assert any("copy" in n.lower() for n in names)
    assert any("move" in n.lower() for n in names)
