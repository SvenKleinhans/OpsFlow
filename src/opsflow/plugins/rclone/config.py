from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from opsflow.core.config import PluginConfig


class RCloneAction(str, Enum):
    """Allowed RClone actions for the plugin."""

    SYNC = "sync"
    COPY = "copy"
    MOVE = "move"


class RCloneOptions(BaseModel):
    """RClone command options."""

    options: dict[str, Any] = Field(default_factory=dict)


class RCloneTask(BaseModel):
    """Definition of a single RClone task."""

    name: str
    description: str | None = None
    action: RCloneAction
    src: str
    dest: str
    options: RCloneOptions | None = None


class RClonePluginConfig(PluginConfig):
    """Configuration model for the RClone plugin."""

    name: str = "RClone"
    max_workers: int = 4
    config_file: str | None = None
    tasks: list[RCloneTask] = Field(default_factory=list)
