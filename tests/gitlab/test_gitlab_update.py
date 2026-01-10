import pytest
import logging
from opsflow.core.models import Severity
from opsflow.core.models.result import Result
from opsflow.core.system import ThreadSafePackageManager
from ..support.fake_pkg_manager import FakePkgManager


def test_run_update_disabled(plugin, gitlab_config, caplog):
    gitlab_config.run_update = False

    with caplog.at_level(logging.INFO):
        plugin.run()

    assert plugin.ctx.all_results() == []


@pytest.mark.parametrize(
    "installed,candidate,expected_msg",
    [
        (None, "16.0.0", "Could not determine installed GitLab version"),
        ("15.0.0", None, "Could not determine candidate GitLab version"),
    ],
)
def test_validate_versions_missing(plugin, installed, candidate, expected_msg):
    assert plugin._validate_versions(installed, candidate) is False

    results = plugin.ctx.all_results()
    assert len(results) == 1
    assert results[0].severity == Severity.ERROR
    assert expected_msg in results[0].message


def test_validate_versions_major_update(plugin):
    assert plugin._validate_versions("15.9.0", "16.0.0") is False

    results = plugin.ctx.all_results()
    assert len(results) == 1
    r = results[0]
    assert r.severity == Severity.WARNING
    assert "Major GitLab update available" in r.message


def test_validate_versions_ok(plugin):
    assert plugin._validate_versions("15.9.0", "15.10.1") is True
    assert plugin.ctx.all_results() == []


def test_is_major_update_invalid_version(plugin):
    assert plugin._is_major_update("not-a-version", "1.0.0") is False


def test_update_without_pkg_manager(plugin):
    plugin.ctx.pkg_manager = None

    assert plugin._update() is False

    results = plugin.ctx.all_results()
    assert len(results) == 1
    assert results[0].severity == Severity.ERROR
    assert "No package manager found" in results[0].message


def test_update_success(plugin, context):
    context.pkg_manager = ThreadSafePackageManager(FakePkgManager())
    context.cmd.run_as_result = lambda *_: None

    assert plugin._update() is True
    assert context.all_results() == []


def test_update_install_failure(plugin, context):
    class Pkg(FakePkgManager):
        def install(self, package: str, version: str | None) -> Result | None:
            return Result(step="Install", severity=Severity.ERROR, message="fail")

    context.pkg_manager = ThreadSafePackageManager(Pkg())

    assert plugin._update() is False

    results = context.all_results()
    assert len(results) == 1
    assert results[0].severity == Severity.ERROR


def test_restart_success(plugin, context):
    context.cmd.run_as_result = lambda *_: None
    assert plugin._restart() is True


def test_restart_failure(plugin, context):
    context.cmd.run_as_result = lambda *_: Result(
        step="Restart", severity=Severity.ERROR, message="fail"
    )

    assert plugin._restart() is False
    assert len(context.all_results()) == 1
