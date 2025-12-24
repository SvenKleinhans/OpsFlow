import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ..config import PluginConfig
from ..models.context import Context

_C = TypeVar("_C", bound=PluginConfig)


class Plugin(ABC, Generic[_C]):
    """Base class for all workflow plugins.

    Every plugin implements `run()` and may optionally override `setup()`
    and `teardown()`.

    Args:
        config (C): Application configuration object passed to all components.
        logger (logging.Logger): Logger dedicated to this plugin.
        ctx (Context): Shared context containing system services.
    """

    name: str = "unnamed"

    def __init__(self, config: _C, logger: logging.Logger, ctx: Context) -> None:
        self.config: _C = config
        self.logger = logger
        self.ctx = ctx

    def setup(self) -> None:
        """Optional initialization executed before run()."""

    @abstractmethod
    def run(self) -> None:
        """Executes the plugin's main task."""

    def teardown(self) -> None:
        """Optional cleanup executed after `run()`."""
