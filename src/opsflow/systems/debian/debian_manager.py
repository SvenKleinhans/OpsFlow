from typing import Optional
from urllib import error, request

from opsflow.core.system import SystemManager
from opsflow.core.models import Result, Severity


class DebianManager(SystemManager):
    def _is_reboot_required(self) -> bool:
        try:
            with open("/var/run/reboot-required", "r"):
                return True
        except FileNotFoundError:
            return False

    def _is_new_stable_os_available(self) -> bool:
        latest = self._get_latest_stable_release()
        current = self._get_os_codename()
        if latest and current:
            return latest.lower() != current.lower()
        return False

    def _get_os_codename(self) -> Optional[str]:
        """Return the OS version codename from /etc/os-release.

        Reads the local `/etc/os-release` file and extracts the value of
        `VERSION_CODENAME`.

        Returns:
            Optional[str]: The OS codename if found, otherwise None.

        Raises:
            Exception: Any unexpected error while reading the file is logged
                and reported via the context.
        """
        try:
            with open("/etc/os-release") as f:
                return next(
                    (
                        line.split("=", 1)[1].strip()
                        for line in f
                        if line.startswith("VERSION_CODENAME=")
                    ),
                    None,
                )
        except Exception as e:
            self.logger.exception("Failed to read /etc/os-release: %s", e)
            self.ctx.add_result(
                Result(
                    step="OS Release Check",
                    severity=Severity.ERROR,
                    message=f"Failed to read /etc/os-release: {e}",
                )
            )
            return None

    def _get_latest_stable_release(self) -> Optional[str]:
        """Return the codename of the latest Debian stable release.

        Fetches the Debian stable `Release` file and extracts the `Codename`
        field.

        Returns:
            Optional[str]: The Debian stable codename if found, otherwise None.

        Raises:
            URLError: Network-related errors are logged and reported as warnings.
            Exception: Unexpected errors are logged and reported as errors.
        """
        url = "https://deb.debian.org/debian/dists/stable/Release"
        try:
            with request.urlopen(url, timeout=5) as r:
                return next(
                    (
                        line.split(":", 1)[1].strip()
                        for line in r.read().decode().splitlines()
                        if line.startswith("Codename:")
                    ),
                    None,
                )
        except error.URLError as e:
            severity = Severity.WARNING
            msg = f"Failed to fetch the latest Debian version: {e}"
        except Exception as e:
            severity = Severity.ERROR
            msg = f"Unexpected error fetching the Debian version: {e}"

        if severity == Severity.WARNING:
            self.logger.warning(msg)
        else:
            self.logger.error(msg)

        self.ctx.add_result(
            Result(
                step="OS Release Check",
                severity=severity,
                message=msg,
            )
        )
        return None
