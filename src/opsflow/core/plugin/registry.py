from ..config import PluginConfig
from ..registry.base import Registry
from .base import Plugin

PluginRegistry = Registry(base_cls=Plugin, default_config=PluginConfig, kind="Plugin")
