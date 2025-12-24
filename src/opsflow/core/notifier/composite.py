from .base import Notifier


class CompositeNotifier:
    """Notifier that sends notifications to multiple backends."""

    def __init__(self):
        """Initializes an empty composite notifier."""
        self._notifiers: list[Notifier] = []

    def add_notifier(self, notifier: Notifier) -> None:
        """Registers a notifier backend.

        Args:
            notifier (Notifier): The notifier to add.
        """
        self._notifiers.append(notifier)

    def notify(self, subject: str, message: str) -> None:
        """Sends a notification to all registered notifiers.

        Args:
            subject (str): Notification subject.
            message (str): Notification body.
        """
        for notifier in self._notifiers:
            notifier.notify(subject, message)
