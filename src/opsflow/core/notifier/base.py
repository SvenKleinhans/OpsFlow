import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ..config import NotifierConfig

_C = TypeVar("_C", bound=NotifierConfig)


class Notifier(ABC, Generic[_C]):
    """Abstract base class for all notification backends."""

    name: str = "unnamed"

    def __init__(self, config: _C, logger: logging.Logger):
        """
        Initialize a Notifier.

        Args:
            config (C): Configuration specific to the notifier.
            logger (logging.Logger): Logger instance for logging messages.
        """
        self.config: _C = config
        self.logger = logger

    @abstractmethod
    def notify(self, subject: str, message: str) -> None:
        """
        Send a notification.

        Args:
            subject (str): Subject of the notification.
            message (str): Body/content of the notification.
        """
