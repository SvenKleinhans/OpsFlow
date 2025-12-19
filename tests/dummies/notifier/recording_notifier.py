from opsflow.core.config import NotifierConfig
from opsflow.core.notifier import Notifier


class RecordingNotifier(Notifier):
    def __init__(self, config: NotifierConfig, logger):
        super().__init__(config, logger)
        self.calls = []

    def notify(self, subject, message):
        self.calls.append((subject, message))
