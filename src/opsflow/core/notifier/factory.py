import logging

from .base import Notifier
from .registry import NotifierRegistry
from ..factory.base import Factory
from ..config.schema import CoreConfig


class NotifierFactory(Factory[Notifier]):
    """Factory for instantiating notifiers based on configuration."""

    def __init__(self, config: CoreConfig, logger: logging.Logger):
        """
        Initialize the NotifierFactory.

        Args:
            config (CoreConfig): Configuration containing notifier settings.
            logger (logging.Logger): Logger instance for notifier logging.
        """
        super().__init__(
            registry=NotifierRegistry, components_cfg=config.notifiers, logger=logger
        )
