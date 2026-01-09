from opsflow.core.models import Result
from opsflow.core.system import PackageManager


class FakePkgManager(PackageManager):
    def get_installed(self, package: str) -> str | None:
        return "15.9.0"

    def get_candidate(self, package: str) -> str | None:
        return "15.10.0"

    def update(self, dry_run: bool = False) -> Result | None:
        return None

    def upgrade(self, dry_run: bool = False) -> Result | None:
        return None

    def install(self, package: str, version: str | None) -> Result | None:
        return None
