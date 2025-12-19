from opsflow.core.plugin import Plugin
from opsflow.core.models import Result, Severity
from .plugin_a import PluginAConfig


class FailingPlugin(Plugin[PluginAConfig]):
    name = "failing_plugin"

    def run(self):
        self.ctx.add_result(
            Result(
                step="Test", message="Executed Plugin failing", severity=Severity.ERROR
            )
        )
        raise RuntimeError("Intentional failure")
