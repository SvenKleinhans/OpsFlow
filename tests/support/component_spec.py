from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ComponentSpec:
    component_cls: type
    config_cls: type
    cfg: Any
    name: str | None = None
