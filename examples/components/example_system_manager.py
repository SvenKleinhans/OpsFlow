from opsflow.core.system import SystemManager


class ExampleSystemManager(SystemManager):
    def _is_new_stable_os_available(self) -> bool:
        # Implement logic to check for new stable OS version
        print("Checking for new stable OS version...")
        return False

    def _is_reboot_required(self) -> bool:
        # Implement logic to check if a reboot is required
        print("Checking if reboot is required...")
        return False
