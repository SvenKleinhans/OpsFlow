"""
Example auto-registered plugin for demonstration purposes.
"""

from opsflow.core.config import PluginConfig
from opsflow.core.plugin import Plugin, PluginRegistry


class ExamplePluginAutoConfig(PluginConfig):
    """Configuration for ExamplePluginAuto."""

    name: str = "ExamplePluginAuto"
    example_option: str = "auto_value"


@PluginRegistry.register(ExamplePluginAutoConfig)
class ExamplePluginAuto(Plugin[ExamplePluginAutoConfig]):
    """An automatically registered example plugin."""

    name = "example_plugin_auto"

    def setup(self) -> None:
        self.logger.info("Setting up ExamplePluginAuto.")

    def run(self) -> None:
        self.logger.info("Running ExamplePluginAuto with option: %s", self.config.example_option)

    def teardown(self) -> None:
        self.logger.info("Tearing down ExamplePluginAuto.")
