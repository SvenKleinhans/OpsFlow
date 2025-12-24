import logging

from ..config.schema import CoreConfig
from ..factory.base import Factory
from ..models.context import Context
from .base import Plugin
from .registry import PluginRegistry


class PluginFactory(Factory[Plugin]):
    """Factory for instantiating plugins based on configuration."""

    def __init__(
        self,
        config: CoreConfig,
        logger: logging.Logger,
        ctx: Context,
    ):
        """
        Initialize the NotifierFactory.

        Args:
            config (CoreConfig): Configuration containing plugin settings.
            logger (logging.Logger): Logger instance for plugin logging.
            ctx (Context): Execution context to be passed to plugins.
        """
        super().__init__(
            registry=PluginRegistry,
            components_cfg=config.plugins,
            logger=logger,
            ctx=ctx,
        )
