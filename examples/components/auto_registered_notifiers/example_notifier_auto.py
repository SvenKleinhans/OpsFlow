"""
Example auto-registered notifier for demonstration purposes.
"""

from opsflow.core.config import NotifierConfig
from opsflow.core.notifier import Notifier, NotifierRegistry


class ExampleNotifierAutoConfig(NotifierConfig):
    """Configuration for ExampleNotifierAuto."""

    name: str = "ExampleNotifierAuto"
    notify_option: str = "auto_notify"


@NotifierRegistry.register(ExampleNotifierAutoConfig)
class ExampleNotifierAuto(Notifier[ExampleNotifierAutoConfig]):
    """An automatically registered example notifier."""

    name = "example_notifier_auto"

    def notify(self, subject: str, message: str) -> None:
        self.logger.info("Auto-notifying with option: %s", self.config.notify_option)
        self.logger.info("Subject: %s", subject)
        self.logger.info("Message: %s", message)
