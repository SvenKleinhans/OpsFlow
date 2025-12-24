import logging
from collections.abc import Generator
from typing import Any, Generic, TypeVar

from ..models.context import Context
from ..registry.base import Registry

_C = TypeVar("_C")  # Component type


class Factory(Generic[_C]):
    """Factory for instantiating components based on a registry and configuration."""

    def __init__(
        self,
        registry: Registry,
        components_cfg: dict[str, Any],
        logger: logging.Logger,
        ctx: Context | None = None,
    ):
        """
        Initialize the Factory.

        Args:
            registry (Registry): Registry containing component classes.
            components_cfg (dict[str, Any]): Configuration containing component settings.
            logger (logging.Logger): Logger instance for component logging.
            ctx (Optional[Context]): Execution context to be passed to components.
        """
        self._components_cfg = components_cfg
        self._logger = logger
        self._registry = registry
        self._ctx = ctx

    def create_all(self) -> Generator[_C, None, None]:
        """
        Instantiate all registered components that are enabled.

        Returns:
            Generator[_C]: Generator yielding component instances.
        """
        for entry in self._registry.entries.values():
            cls = entry.component_cls
            name = getattr(cls, "name", cls.__name__)
            cfg = self._components_cfg.get(name)

            if not cfg or not getattr(cfg, "enabled", False):
                continue

            child_logger = self._logger.getChild(name)
            if self._ctx:
                yield cls(cfg, child_logger, self._ctx)
            else:
                yield cls(cfg, child_logger)
