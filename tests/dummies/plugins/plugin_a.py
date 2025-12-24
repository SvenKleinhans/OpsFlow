from opsflow.core.config import PluginConfig
from opsflow.core.models import Result, Severity
from opsflow.core.plugin import Plugin


class PluginAConfig(PluginConfig):
    value: int = 1
    enabled: bool = True


class PluginA(Plugin[PluginAConfig]):
    name = "plugin_a"

    def __init__(self, config, logger, ctx):
        super().__init__(config, logger, ctx)
        self.result = None

    def setup(self):
        pass

    def run(self):
        self.ctx.add_result(
            Result(step="Test", message="Executed Plugin A", severity=Severity.INFO)
        )
        self.result = f"A:{self.config.value}"

    def teardown(self):
        pass
