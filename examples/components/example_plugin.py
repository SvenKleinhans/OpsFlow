from opsflow.core.config import PluginConfig
from opsflow.core.plugin import Plugin


class ExamplePluginConfig(PluginConfig):
    """Configuration for the ExamplePlugin."""

    name: str = "ExamplePlugin"
    example_option: str = "default_value"


class ExamplePlugin(Plugin[ExamplePluginConfig]):
    """An example plugin demonstrating the Plugin interface."""

    name = "example_plugin"

    def setup(self) -> None:
        """Optional initialization executed before run()."""
        self.logger.info("Setting up ExamplePlugin.")

    def run(self) -> None:
        """Run the example plugin's main task."""
        self.logger.info("Running ExamplePlugin with option: %s", self.config.example_option)
        # Implement the main logic of the plugin here

    def teardown(self) -> None:
        """Optional cleanup executed after `run()`."""
        self.logger.info("Tearing down ExamplePlugin.")
