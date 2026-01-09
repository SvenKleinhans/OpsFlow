from abc import ABC, abstractmethod
import threading

from ..models.result import Result


class PackageManager(ABC):
    """Abstract base class for package management operations.

    This interface provides a minimal, generic abstraction over system-level
    package managers (e.g. apt, yum, zypper). It must not contain any
    product- or application-specific logic.
    """

    @abstractmethod
    def update(self, dry_run: bool = False) -> Result | None:
        """Update the local package metadata.

        Args:
            dry_run (bool): If True, simulate the operation without making changes.

        Returns:
            Optional[Result]: A Result object if an issue occurred, otherwise None.
        """

    @abstractmethod
    def upgrade(self, dry_run: bool = False) -> Result | None:
        """Upgrade installed packages to newer available versions.

        Args:
            dry_run (bool): If True, simulate the operation without making changes.

        Returns:
            Optional[Result]: A Result object if an issue occurred, otherwise None.
        """

    @abstractmethod
    def install(self, package: str, version: str | None) -> Result | None:
        """Install or upgrade a specific package.

        If a version is provided, the package manager should attempt to install
        exactly that version. If no version is given, the latest available
        candidate version should be installed.

        Args:
            package (str): Name of the package to install.
            version (str | None): Optional package version to install.

        Returns:
            Result | None: A Result object describing an error or warning if the
            operation failed or produced an issue, otherwise None.
        """

    @abstractmethod
    def get_installed(self, package: str) -> str | None:
        """Return the currently installed version of a package.

        Args:
            package (str): Name of the package.

        Returns:
            str | None: The installed version string, or None if the package
            is not installed.
        """

    @abstractmethod
    def get_candidate(self, package: str) -> str | None:
        """Return the candidate version of a package.

        The candidate version is the version that would be installed if an
        install or upgrade operation were performed.

        Args:
            package (str): Name of the package.

        Returns:
            str | None: The candidate version string, or None if no candidate
            is available.
        """


class ThreadSafePackageManager:
    """Thread-safe wrapper around a PackageManager.

    All method calls are synchronized to allow safe concurrent access from multiple threads.
    This wrapper does not modify the behavior of the underlying PackageManager, only adds thread-safety.
    """

    def __init__(self, pm: PackageManager):
        self._pm = pm
        self._lock = threading.Lock()

    def install(self, package: str, version: str | None = None):
        """Install or upgrade a specific package.

        If a version is provided, attempts to install exactly that version.
        If no version is given, installs the latest available candidate version.

        Args:
            package (str): Name of the package to install.
            version (str | None): Optional package version to install.

        Returns:
            Result | None: A Result object describing an error or warning if the
            operation failed or produced an issue, otherwise None.
        """
        with self._lock:
            return self._pm.install(package, version)

    def get_installed(self, package: str) -> str | None:
        """Return the currently installed version of a package.

        Args:
            package (str): Name of the package.

        Returns:
            str | None: The installed version string, or None if the package
            is not installed.
        """
        with self._lock:
            return self._pm.get_installed(package)

    def get_candidate(self, package: str) -> str | None:
        """Return the candidate version of a package.

        The candidate version is the version that would be installed if an
        install or upgrade operation were performed.

        Args:
            package (str): Name of the package.

        Returns:
            str | None: The candidate version string, or None if no candidate
            is available.
        """
        with self._lock:
            return self._pm.get_candidate(package)
