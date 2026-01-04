import builtins
import io
from urllib import error, request

from opsflow.systems.debian.debian_manager import DebianManager
from opsflow.core.models import Severity


def test_reboot_required(monkeypatch, make_manager):
    monkeypatch.setattr(builtins, "open", lambda *a, **k: io.StringIO(""))
    mgr = make_manager(DebianManager)
    assert mgr._is_reboot_required() is True


def test_os_codename(monkeypatch, make_manager):
    data = "VERSION_CODENAME=bookworm\n"
    monkeypatch.setattr(builtins, "open", lambda *a, **k: io.StringIO(data))

    mgr = make_manager(DebianManager)
    assert mgr._get_os_codename() == "bookworm"


def test_latest_stable(monkeypatch, make_manager):
    content = b"Codename: trixie\n"
    monkeypatch.setattr(
        request,
        "urlopen",
        staticmethod(lambda *a, **k: io.BytesIO(content)),
    )

    mgr = make_manager(DebianManager)
    assert mgr._get_latest_stable_release() == "trixie"


def test_latest_stable_network_error(monkeypatch, make_manager, context):
    monkeypatch.setattr(
        request,
        "urlopen",
        staticmethod(lambda *a, **k: (_ for _ in ()).throw(error.URLError("net"))),
    )

    mgr = make_manager(DebianManager)
    assert mgr._get_latest_stable_release() is None

    r = context.all_results()[0]
    assert r.severity == Severity.WARNING
