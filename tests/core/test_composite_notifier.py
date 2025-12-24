import pytest

from opsflow.core.notifier.composite import CompositeNotifier

from ..dummies.notifier.dummy_notifier import (
    DummyNotifier,
    DummyNotifierConfig,
)
from ..dummies.notifier.raising_notifier import RaisingNotifier
from ..dummies.notifier.recording_notifier import RecordingNotifier


def test_composite_forwards_message_to_all_notifiers(logger):
    """Composite should forward notifications to every added notifier."""
    comp = CompositeNotifier()
    cfg = DummyNotifierConfig()

    dummy = DummyNotifier(cfg, logger)
    recorder = RecordingNotifier(cfg, logger)

    comp.add_notifier(dummy)
    comp.add_notifier(recorder)

    comp.notify("subject", "payload")

    assert dummy.last_message == "DUMMY:payload"
    assert recorder.calls == [("subject", "payload")]


def test_composite_stops_on_exception_and_skips_remaining(logger):
    """If a notifier raises, composite should propagate the error and stop processing."""
    comp = CompositeNotifier()
    cfg = DummyNotifierConfig()

    raising = RaisingNotifier(cfg, logger)
    recorder = RecordingNotifier(cfg, logger)

    comp.add_notifier(raising)
    comp.add_notifier(recorder)

    with pytest.raises(RuntimeError):
        comp.notify("s", "m")

    assert recorder.calls == []  # must not be called


def test_composite_calls_previous_notifiers_before_exception(logger):
    """If the second notifier raises, the first one must still have been called."""
    comp = CompositeNotifier()
    cfg = DummyNotifierConfig()

    recorder = RecordingNotifier(cfg, logger)
    raising = RaisingNotifier(cfg, logger)

    comp.add_notifier(recorder)
    comp.add_notifier(raising)

    with pytest.raises(RuntimeError):
        comp.notify("alpha", "beta")

    assert recorder.calls == [("alpha", "beta")]
