from opsflow.core.notifier import Notifier
from opsflow.core.config import NotifierConfig


class DummyNotifierConfig(NotifierConfig):
    channel: str = "#testing"
    enabled: bool = True


class DummyNotifier(Notifier):
    name = "dummy"

    def __init__(self, config: DummyNotifierConfig, logger):
        super().__init__(config, logger)
        self.last_message = None

    def notify(self, subject: str, message: str) -> None:
        self.last_message = f"DUMMY:{message}"
