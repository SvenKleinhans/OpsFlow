from .base import Plugin
from ..registry.base import Registry
from ..config import PluginConfig


PluginRegistry = Registry(base_cls=Plugin, default_config=PluginConfig, kind="Plugin")
