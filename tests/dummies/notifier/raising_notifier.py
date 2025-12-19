from opsflow.core.config import NotifierConfig
from opsflow.core.notifier import Notifier


class RaisingNotifier(Notifier):
    def __init__(self, config: NotifierConfig, logger):
        super().__init__(config, logger)

    def notify(self, subject, message):
        raise RuntimeError("intentional")
