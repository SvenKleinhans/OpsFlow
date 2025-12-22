from opsflow.core.notifier import Notifier
from opsflow.core.config import NotifierConfig


class ExampleNotifierConfig(NotifierConfig):
    """Configuration for the ExampleNotifier."""

    name: str = "ExampleNotifier"
    notify_option: str = "default_notify_value"


class ExampleNotifier(Notifier[ExampleNotifierConfig]):
    """An example notifier demonstrating the Notifier interface."""

    name = "example_notifier"

    def notify(self, subject: str, message: str) -> None:
        """Send a notification with the given subject and message."""
        self.logger.info("Notifying with option: %s", self.config.notify_option)
        self.logger.info("Subject: %s", subject)
        self.logger.info("Message: %s", message)
        # Implement the notification logic here
