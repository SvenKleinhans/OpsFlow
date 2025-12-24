from opsflow.core.models import Result, Severity
from opsflow.core.system import PackageManager


class ExamplePackageManager(PackageManager):
    def update(self, dry_run: bool = False) -> Result | None:
        if dry_run:
            print("Simulating package list update...")
            return None

        print("Updating package lists...")
        # Implement the actual update logic here
        # For example, run system commands to update package lists
        return Result(
            step="update",
            severity=Severity.INFO,
            message="Package lists updated successfully.",
        )

    def upgrade(self, dry_run: bool = False) -> Result | None:
        if dry_run:
            print("Simulating package upgrade...")
            return None

        print("Upgrading packages...")
        # Implement the actual upgrade logic here
        # For example, run system commands to upgrade packages
        return Result(
            step="upgrade",
            severity=Severity.INFO,
            message="Packages upgraded successfully.",
        )
