import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

import rclone as rc_adapter

from opsflow.core.plugin import Plugin
from opsflow.core.models import Result, Severity

from .config import RClonePluginConfig, RCloneAction, RCloneTask


class RClonePlugin(Plugin[RClonePluginConfig]):
    """Plugin to execute rclone tasks in parallel with OpsFlow."""

    name = "rclone"

    def __init__(self, config: RClonePluginConfig, logger: logging.Logger, ctx) -> None:
        """
        Initialize the RClone plugin.

        Args:
            config (RClonePluginConfig): Plugin configuration containing tasks and global settings.
            logger (logging.Logger): Logger instance for plugin logging.
            ctx (Context): Workflow execution context.
        """
        super().__init__(config, logger, ctx)
        self._lock = threading.Lock()
        self.logger.debug("RClonePlugin initialized")

    def run(self) -> None:
        """Run all configured RClone tasks in parallel using ThreadPoolExecutor."""
        if not self.config.tasks:
            self.logger.info("No rclone tasks configured.")
            return

        self.logger.debug(
            f"Starting ThreadPoolExecutor with max_workers={self.config.max_workers}"
        )
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_task = {
                executor.submit(self._run_task, task): task
                for task in self.config.tasks
            }
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                desc = f" ({task.description})" if task.description else ""
                try:
                    future.result()
                    self.logger.debug(
                        f"Task '{task.name}'{desc} completed successfully {task.src} → {task.dest}"
                    )
                except Exception as e:
                    self.logger.exception(
                        f"Unhandled exception in task '{task.name}'{desc}: {e}"
                    )

    def _run_task(self, task: RCloneTask) -> Optional[rc_adapter.CommandResult]:
        """
        Execute a single RClone task.

        Args:
            task (RCloneTask): The task to execute.

        Returns:
            Optional[CommandResult]: Result of the rclone command.
        """
        step = (
            f"RClone {task.action.value.capitalize()} - {task.name or 'Unnamed Task'}"
        )
        desc = f" ({task.description})" if task.description else ""
        self.logger.debug(f"Starting task '{task.name}'{desc} {task.src} → {task.dest}")

        rc_config = rc_adapter.RCloneConfig(
            config_file=(
                Path(self.config.config_file) if self.config.config_file else None
            ),
            default_flags=self._default_flags_from_ctx(),
        )
        rc = rc_adapter.RClone(rc_config)

        try:
            if task.action == RCloneAction.SYNC:
                cmd_result = self._sync(rc, task)
            elif task.action == RCloneAction.COPY:
                cmd_result = self._copy(rc, task)
            elif task.action == RCloneAction.MOVE:
                cmd_result = self._move(rc, task)
            else:
                raise ValueError(f"Unsupported RClone action: {task.action}")

            self._add_result(step, cmd_result)
            self.logger.debug(f"Task completed: '{task.name}'{desc}")
            return cmd_result

        except Exception as e:
            self.logger.exception(
                f"Error executing RClone task '{task.name}'{desc}: {e}"
            )
            self._add_result(step, None, f"Exception: {e}")
            return None

    def _default_flags_from_ctx(self) -> list[str]:
        """
        Generate default rclone flags based on the workflow context.

        Returns:
            list[str]: List of default flags for rclone commands.
        """
        flags: list[str] = []
        if getattr(self.ctx, "dry_run", False):
            flags.append("--dry-run")
            self.logger.debug("Dry-run enabled, adding --dry-run flag")
        return flags

    def _add_result(
        self,
        step_name: str,
        cmd_result: Optional[rc_adapter.CommandResult],
        exception_message: Optional[str] = None,
    ) -> None:
        """
        Add a task result to the workflow context in a thread-safe manner.

        Args:
            step_name (str): Name of the step.
            cmd_result (Optional[CommandResult]): Result of the rclone command.
            exception_message (Optional[str]): Exception message if the task failed.
        """
        if cmd_result:
            severity = (
                Severity.INFO
                if cmd_result.success
                else (Severity.ERROR if cmd_result.errors else Severity.WARNING)
            )
            message_parts = [
                f"Return code: {cmd_result.return_code}",
                f"Files transferred: {cmd_result.files_transferred}",
                f"Bytes transferred: {cmd_result.bytes_transferred}",
                f"Duration: {cmd_result.duration_seconds:.2f}s",
            ]
            if cmd_result.errors:
                message_parts.append(f"Errors: {[str(e) for e in cmd_result.errors]}")
            if cmd_result.stdout:
                message_parts.append(f"Stdout: {cmd_result.stdout}")
            if cmd_result.stderr:
                message_parts.append(f"Stderr: {cmd_result.stderr}")
            message = "\n".join(message_parts)
        else:
            severity = Severity.ERROR
            message = exception_message or "Unknown error executing RClone task."

        plugin_result = Result(step=step_name, severity=severity, message=message)
        with self._lock:
            self.ctx.add_result(plugin_result)
            self.logger.debug(
                f"Result added for step '{step_name}' with severity {severity.name}"
            )

    @staticmethod
    def _sync(rc: rc_adapter.RClone, task: RCloneTask) -> rc_adapter.CommandResult:
        """
        Execute rclone sync for a given task.

        Args:
            rc (RClone): RClone instance.
            task (RCloneTask): The task to execute.

        Returns:
            CommandResult: Result of the rclone sync command.
        """
        return __import__("asyncio").run(rc.sync(task.src, task.dest, task.options))

    @staticmethod
    def _copy(rc: rc_adapter.RClone, task: RCloneTask) -> rc_adapter.CommandResult:
        """
        Execute rclone copy for a given task.

        Args:
            rc (RClone): RClone instance.
            task (RCloneTask): The task to execute.

        Returns:
            CommandResult: Result of the rclone copy command.
        """
        return __import__("asyncio").run(rc.copy(task.src, task.dest, task.options))

    @staticmethod
    def _move(rc: rc_adapter.RClone, task: RCloneTask) -> rc_adapter.CommandResult:
        """
        Execute rclone move for a given task.

        Args:
            rc (RClone): RClone instance.
            task (RCloneTask): The task to execute.

        Returns:
            CommandResult: Result of the rclone move command.
        """
        return __import__("asyncio").run(rc.move(task.src, task.dest, task.options))
