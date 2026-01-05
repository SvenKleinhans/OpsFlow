from collections.abc import Callable
from pathlib import Path
import sys
from typing import Generic, TypeVar

from .entry import RegistryEntry

_C = TypeVar("_C")
_CFG = TypeVar("_CFG")


class Registry(Generic[_C, _CFG]):
    """
    Generic registry for component classes and their associated configuration classes.

    The registry enforces a common contract:
    - Components must inherit from a given base class.
    - Components must define a unique, non-default ``name`` attribute.
    - Each component is registered together with a configuration class and metadata.

    This class is intended to be specialized for concrete component types
    (e.g. Plugin, Notifier, System) by providing the appropriate base class
    and default configuration.
    """

    def __init__(
        self,
        base_cls: type[_C],
        default_config: type[_CFG],
        kind: str,
    ) -> None:
        """
        Initialize the registry.

        Args:
            base_cls: Base class that all registered components must inherit from.
            default_config: Default configuration class used if none is provided.
            kind: Human-readable component kind used in error messages.
        """
        self._base_cls: type[_C] = base_cls
        self._default_config: type[_CFG] = default_config
        self._kind: str = kind
        self.entries: dict[str, RegistryEntry[_C, _CFG]] = {}

    def register(
        self,
        config: type[_CFG] | None = None,
        description: str = "",
    ) -> Callable[[type[_C]], type[_C]]:
        """
        Decorator for registering a component class.

        Args:
            config: Optional configuration class. If not provided, the registry's
                default configuration class is used.
            description: Optional human-readable description of the component.

        Returns:
            A class decorator that registers the decorated component.
        """

        def wrapper(cls: type[_C]) -> type[_C]:
            self.register_class(cls, config=config, description=description)
            return cls

        return wrapper

    def register_class(
        self,
        cls: type[_C],
        config: type[_CFG] | None,
        description: str = "",
    ) -> None:
        """
        Register a component class manually.

        Args:
            cls: Component class to register.
            config: Optional configuration class. If not provided, the registry's
                default configuration class is used.
            description: Optional human-readable description of the component.

        Raises:
            TypeError: If the class does not inherit from the required base class.
            ValueError: If the class does not define a valid ``name`` attribute
                or if a component with the same name is already registered.
        """
        if not issubclass(cls, self._base_cls):
            raise TypeError(
                f"{cls.__name__} must inherit from {self._base_cls.__name__}"
            )

        name = getattr(cls, "name", None)
        if not name or name == "unnamed":
            raise ValueError(f"{self._kind} {cls.__name__} must define a valid 'name'")

        existing = self.entries.get(name)
        if existing is not None:
            if self._origin_file(existing.component_cls) == self._origin_file(cls):
                return

            raise ValueError(
                f"{self._kind} '{name}' already registered "
                f"from {self._origin_file(existing.component_cls)}"
            )

        self.entries[name] = RegistryEntry(
            component_cls=cls,
            config_cls=config or self._default_config,
            description=description,
        )

    @staticmethod
    def _origin_file(cls_type: type) -> Path | None:
        """Return the resolved source file path of a class.

        The path is derived from the module in which the class was defined.
        This can be used to detect whether two classes originate from the same
        source file even if they were imported under different module names.

        Args:
            cls_type: Class whose defining module should be inspected.

        Returns:
            The resolved path to the module's source file, or ``None`` if the
            module is not loaded or does not define a ``__file__`` attribute.
        """
        mod = sys.modules.get(cls_type.__module__)
        if not mod:
            return None

        file = getattr(mod, "__file__", None)
        if not file:
            return None

        return Path(file).resolve()
