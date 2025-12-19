from opsflow.core.plugin import Plugin
from opsflow.core.models import Result, Severity
from opsflow.core.config import PluginConfig


class PluginBConfig(PluginConfig):
    flag: bool = True
    enabled: bool = True


class PluginB(Plugin[PluginBConfig]):
    name = "plugin_b"

    def __init__(self, config, logger, ctx):
        super().__init__(config, logger, ctx)
        self.result = None

    def setup(self):
        pass

    def run(self):
        self.ctx.add_result(
            Result(step="Test", message="Executed Plugin B", severity=Severity.INFO)
        )
        self.result = f"B:{self.config.flag}"

    def teardown(self):
        pass
