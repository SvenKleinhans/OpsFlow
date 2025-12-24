import logging
from abc import ABC, abstractmethod
from collections.abc import Callable

from ..models.context import Context
from ..models.result import Result, Severity


class PackageManager(ABC):
    """Abstract base class for package management operations."""

    @abstractmethod
    def update(self, dry_run: bool = False) -> Result | None:
        """Update package metadata.

        Args:
            dry_run (bool): If True, simulate the operation without making changes.

        Returns:
            Optional[Result]: A Result object if an issue occurred, otherwise None.
        """

    @abstractmethod
    def upgrade(self, dry_run: bool = False) -> Result | None:
        """Upgrade installed packages.

        Args:
            dry_run (bool): If True, simulate the operation without making changes.

        Returns:
            Optional[Result]: A Result object if an issue occurred, otherwise None.
        """


class SystemManager(ABC):
    """Abstract base class to manage system updates, upgrades, and OS health checks."""

    def __init__(
        self,
        pkg_manager: PackageManager,
        pre_update: list[Callable] | None = None,
        post_update: list[Callable] | None = None,
    ):
        """Initialize the system manager.

        Args:
            pkg_manager (PackageManager): Package manager used for updates/upgrades.
            pre_update (Optional[List[Callable]]): Callables to execute before updates.
            post_update (Optional[List[Callable]]): Callables to execute after updates.
        """
        self.pkg_manager = pkg_manager
        self.pre_update = pre_update or []
        self.post_update = post_update or []

        self.logger: logging.Logger
        self.ctx: Context

    def _attach_runtime(self, logger: logging.Logger, ctx: Context) -> None:
        """Attach runtime components to the system manager.

        Args:
            logger (logging.Logger): Logger instance for output.
            ctx (Context): Contextual information for the operations.
        """
        self.logger = logger
        self.ctx = ctx

    def update(self) -> None:
        """Perform system update and upgrade with pre- and post-update hooks.

        Exceptions in hooks or package operations are caught and converted into `Result` objects.
        """
        self.logger.info("Starting system update...")

        # Pre-update hooks
        for func in self.pre_update:
            try:
                self.logger.debug(f"Executing pre-update hook: {func.__name__}")
                func()
            except Exception as e:
                self.logger.exception(f"Pre-update hook {func.__name__} failed: {e}")
                self.ctx.add_result(
                    Result(
                        step=f"Pre-update hook {func.__name__}",
                        severity=Severity.WARNING,
                        message=str(e),
                    )
                )
        # PackageManager update
        try:
            self.ctx.add_result(self.pkg_manager.update(dry_run=self.ctx.dry_run))
        except Exception as e:
            self.logger.exception(f"PackageManager.update() failed: {e}")
            self.ctx.add_result(
                Result(step="Package update", severity=Severity.ERROR, message=str(e))
            )

        # PackageManager upgrade
        try:
            self.ctx.add_result(self.pkg_manager.upgrade(dry_run=self.ctx.dry_run))
        except Exception as e:
            self.logger.exception(f"PackageManager.upgrade() failed: {e}")
            self.ctx.add_result(
                Result(step="Package upgrade", severity=Severity.ERROR, message=str(e))
            )

        self.logger.info("System update completed successfully.")

        # Post-update hooks
        for func in self.post_update:
            try:
                self.logger.debug(f"Executing post-update hook: {func.__name__}")
                func()
            except Exception as e:
                self.logger.exception(f"Post-update hook {func.__name__} failed: {e}")
                self.ctx.add_result(
                    Result(
                        step=f"Post-update hook {func.__name__}",
                        severity=Severity.WARNING,
                        message=str(e),
                    )
                )

    def check_reboot_required(self) -> None:
        """Check if the system requires a reboot and convert to a Result object."""
        if self._is_reboot_required():
            message = "System requires a reboot"
            self.logger.warning(message)
            self.ctx.add_result(
                Result(step="Reboot Check", severity=Severity.WARNING, message=message)
            )

    def check_new_stable_available(self) -> None:
        """Check if a new stable OS release is available and convert to a Result object."""
        if self._is_new_stable_os_available():
            message = "A new stable OS release is available"
            self.logger.warning(message)
            self.ctx.add_result(
                Result(step="OS Upgrade Check", severity=Severity.WARNING, message=message)
            )

    @abstractmethod
    def _is_reboot_required(self) -> bool:
        """Check if a system reboot is required.

        This method should be implemented per operating system to determine
        if any pending updates or changes require a system reboot.

        Returns:
            bool: True if a system reboot is required, False otherwise.
        """

    @abstractmethod
    def _is_new_stable_os_available(self) -> bool:
        """Check if a new stable OS release is available.

        This method should be implemented per operating system to detect
        whether an upgrade to a new stable release is available.

        Returns:
            bool: True if a new stable release is available, False otherwise.
        """
