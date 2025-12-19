from dataclasses import dataclass
from typing import Type, Generic, TypeVar

_C = TypeVar("_C")  # Component type (Plugin, Notifier, etc.)
_CFG = TypeVar("_CFG")  # Configuration type


@dataclass
class RegistryEntry(Generic[_C, _CFG]):
    """
    Represents a single entry in a component registry.

    Each entry links a component class (e.g., Plugin or Notifier)
    with its corresponding configuration class.
    Optional metadata can be added, such as a description.

    Attributes:
        component_cls (Type[_C]): The class of the component being registered.
        config_cls (Type[_CFG]): The Pydantic configuration class associated with the component.
        description (str): Optional human-readable description of the component.
    """

    component_cls: Type[_C]
    config_cls: Type[_CFG]
    description: str = ""
