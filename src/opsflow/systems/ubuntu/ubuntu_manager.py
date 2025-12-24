import os

from opsflow.core.models import Result, Severity
from opsflow.core.system import SystemManager
from opsflow.core.utils import CommandRunner


class UbuntuManager(SystemManager):
    def _is_reboot_required(self) -> bool:
        return os.path.exists("/var/run/reboot-required")

    def _is_new_stable_os_available(self) -> bool:
        try:
            r = CommandRunner.run(
                ["do-release-upgrade", "-c"],
                env={"LANG": "C", "LC_ALL": "C"},
                use_sudo=False,
            )
            return r.returncode == 0 and "new release" in (r.stdout or "").lower()
        except FileNotFoundError:
            msg = "do-release-upgrade command not found."
            severity = Severity.WARNING
        except Exception as e:
            msg = f"Error checking for Ubuntu release: {e}"
            severity = Severity.ERROR

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
        return False
