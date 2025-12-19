import logging
import subprocess
from pathlib import Path
from typing import Optional

from ..models.result import Result, Severity


class CommandRunner:
    """Utility class for executing shell commands with logging support."""

    _logger: Optional[logging.Logger] = None
    _dry_run: bool = False

    @classmethod
    def configure(cls, dry_run: bool, logger: logging.Logger) -> None:
        """Configures the command runner.

        Args:
            dry_run (bool): If True, commands will not be executed.
            logger (logging.Logger): Logger used for command tracing.
        """
        cls._dry_run = dry_run
        cls._logger = logger

        if logger:
            logger.debug("CommandRunner configured (dry_run=%s)", dry_run)

    @classmethod
    def run(
        cls,
        command: list[str],
        env: Optional[dict[str, str]] = None,
        working_directory: Optional[Path] = None,
        check: bool = False,
        use_sudo: bool = True,
    ) -> subprocess.CompletedProcess:
        """Executes a shell command.

        Args:
            command (list[str]): Command to execute.
            env (Optional[dict[str, str]]): Environment variables for the command.
            working_directory (Optional[Path]): Directory in which to run the command.
            check (bool): If True, raises CalledProcessError on non-zero exit code.
            use_sudo (bool): Whether to prepend 'sudo' to the command.

        Returns:
            subprocess.CompletedProcess: The process result.

        Raises:
            RuntimeError: If the runner is not configured.
            subprocess.CalledProcessError: If check=True and the command fails.
        """
        if cls._logger is None:
            raise RuntimeError("CommandRunner not configured. Call configure() first.")

        logger = cls._logger

        cmd = command.copy()
        if use_sudo:
            cmd.insert(0, "sudo")

        logger.debug("RUN: %s", " ".join(cmd))

        if cls._dry_run:
            logger.info("Dry-run: skipping execution")
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            cwd=str(working_directory) if working_directory else None,
            env=env,
        )

        if result.stdout:
            logger.debug("STDOUT: %s", result.stdout.strip())
        if result.stderr:
            logger.debug("STDERR: %s", result.stderr.strip())

        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, output=result.stdout, stderr=result.stderr
            )

        return result

    @classmethod
    def run_as_result(
        cls,
        command: list[str],
        step: str,
        env: Optional[dict[str, str]] = None,
        working_directory: Optional[Path] = None,
        use_sudo: bool = True,
    ) -> Optional[Result]:
        """Executes a command and returns a Result object on failure.

        Args:
            command (list[str]): Command to execute.
            step (str): The step name reported in the result object.
            env (Optional[dict[str, str]]): Environment variables for the command.
            working_directory (Optional[Path]): Directory in which to run the command.
            use_sudo (bool): Whether to prepend sudo.

        Returns:
            Optional[Result]: Result object on failure, otherwise None.
        """
        res = cls.run(
            command,
            env=env,
            working_directory=working_directory,
            check=False,
            use_sudo=use_sudo,
        )

        if res.returncode != 0:
            message = f"Command {' '.join(command)} failed: {res.stderr.strip()}"
            severity = Severity.ERROR

            if cls._logger:
                cls._logger.error(message)

            return Result(step=step, severity=severity, message=message)

        return None
