import sys
from typing import Protocol, cast
from pathlib import Path
from opsflow.core.utils.module_loader import ModuleLoader


class _PluginModule(Protocol):
    OK: bool
    VALUE: int
    X: int


def modules_from_dir(path: Path) -> dict[str, object]:
    path = path.resolve()
    result = {}
    for name, mod in sys.modules.items():
        file = getattr(mod, "__file__", None)
        if file and Path(file).resolve().parent == path:
            result[name] = mod
    return result


def test_load_directory_loads_modules(tmp_path):
    pkg_dir = tmp_path / "plugins"
    pkg_dir.mkdir()
    (pkg_dir / "a.py").write_text("VALUE = 123")

    ModuleLoader.load_from_directory(str(pkg_dir))

    mods = modules_from_dir(pkg_dir)
    assert len(mods) == 1

    mod = next(iter(mods.values()))
    mod = cast(_PluginModule, mod)
    assert mod.VALUE == 123


def test_load_directory_ignores_non_python_files(tmp_path):
    pkg_dir = tmp_path / "plugins"
    pkg_dir.mkdir()
    (pkg_dir / "good.py").write_text("OK = True")
    (pkg_dir / "ignored.txt").write_text("NOPE")

    ModuleLoader.load_from_directory(str(pkg_dir))

    mods = modules_from_dir(pkg_dir)
    assert len(mods) == 1

    mod = next(iter(mods.values()))
    mod = cast(_PluginModule, mod)
    assert mod.OK is True


def test_load_directory_is_idempotent(tmp_path):
    pkg_dir = tmp_path / "plugins"
    pkg_dir.mkdir()
    (pkg_dir / "a.py").write_text("X = 1")

    ModuleLoader.load_from_directory(str(pkg_dir))
    first = modules_from_dir(pkg_dir)

    ModuleLoader.load_from_directory(str(pkg_dir))
    second = modules_from_dir(pkg_dir)

    assert first.keys() == second.keys()
    assert cast(_PluginModule, next(iter(second.values()))).X == 1
