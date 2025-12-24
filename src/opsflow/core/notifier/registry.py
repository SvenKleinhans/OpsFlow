from ..config.schema import NotifierConfig
from ..registry.base import Registry
from .base import Notifier

NotifierRegistry = Registry(
    base_cls=Notifier,
    default_config=NotifierConfig,
    kind="notifier",
)
