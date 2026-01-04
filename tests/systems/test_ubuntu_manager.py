import os
from types import SimpleNamespace

from opsflow.systems.ubuntu.ubuntu_manager import UbuntuManager
from opsflow.core.utils import CommandRunner
from opsflow.core.models import Severity


def test_reboot_required(monkeypatch, make_manager):
    monkeypatch.setattr(os.path, "exists", lambda p: True)
    mgr = make_manager(UbuntuManager)
    assert mgr._is_reboot_required() is True


def test_new_release_available(monkeypatch, make_manager):
    fake = SimpleNamespace(returncode=0, stdout="new release available")
    monkeypatch.setattr(CommandRunner, "run", staticmethod(lambda *a, **k: fake))

    mgr = make_manager(UbuntuManager)
    assert mgr._is_new_stable_os_available() is True


def test_release_check_file_not_found(monkeypatch, make_manager, context):
    def raise_fn(*a, **k):
        raise FileNotFoundError()

    monkeypatch.setattr(CommandRunner, "run", staticmethod(raise_fn))

    mgr = make_manager(UbuntuManager)
    assert mgr._is_new_stable_os_available() is False

    r = context.all_results()[0]
    assert r.severity == Severity.WARNING
