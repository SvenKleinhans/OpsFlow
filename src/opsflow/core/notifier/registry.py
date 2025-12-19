from .base import Notifier
from ..config.schema import NotifierConfig
from ..registry.base import Registry


NotifierRegistry = Registry(
    base_cls=Notifier,
    default_config=NotifierConfig,
    kind="notifier",
)
