# dummy components for testing
from ..dummies.notifier.dummy_notifier import (
    DummyNotifier,
    DummyNotifierConfig,
)

from ..support.component_spec import ComponentSpec


def test_enabled_notifier(make_components):
    notifier = make_components(
        ComponentSpec(
            component_cls=DummyNotifier,
            config_cls=DummyNotifierConfig,
            cfg=DummyNotifierConfig(enabled=True, channel="#SLACK"),
        )
    )[0]

    notifier.notify("subj", "msg")
    assert notifier.last_message == "DUMMY:msg"
