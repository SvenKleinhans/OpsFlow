from opsflow.systems.apt.apt_manager import AptManager
from opsflow.core.utils import CommandRunner
from opsflow.core.models import Result, Severity


def test_run_apt_adds_simulate(monkeypatch):
    captured = {}

    def fake_run(args, step):
        captured["args"] = args
        return None

    monkeypatch.setattr(CommandRunner, "run_as_result", staticmethod(fake_run))

    AptManager._run_apt(["apt-get", "upgrade", "-y"], "step", dry_run=True)

    assert "--simulate" in captured["args"]
    assert captured["args"][1] == "--simulate"


def test_upgrade_stops_on_first_result(monkeypatch, make_manager):
    calls = []

    def fake_run(args, step, dry_run):
        calls.append(step)
        return Result(step=step, severity=Severity.INFO, message="ok")

    monkeypatch.setattr(AptManager, "_run_apt", staticmethod(fake_run))

    mgr = make_manager(AptManager)
    res = mgr.upgrade(dry_run=False)

    assert res.step == "System Upgrade"
    assert calls == ["System Upgrade"]
