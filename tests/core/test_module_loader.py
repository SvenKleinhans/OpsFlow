import sys

from opsflow.core.utils.module_loader import ModuleLoader


def _cleanup_module_names(*names):
    """Remove imported modules from sys.modules to avoid cross-test pollution."""
    for name in names:
        sys.modules.pop(name, None)


def test_load_directory_with_explicit_package_name(tmp_path):
    """Modules should load when a package name is explicitly provided."""
    pkg_dir = tmp_path / "mypkg"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").write_text("""# package init""")
    (pkg_dir / "a.py").write_text("""VALUE = 123""")

    try:
        ModuleLoader.load_from_directory(str(pkg_dir), package="mypkg")

        assert "mypkg.a" in sys.modules
        mod = sys.modules["mypkg.a"]
        assert mod.VALUE == 123
    finally:
        _cleanup_module_names("mypkg.a", "mypkg")


def test_load_directory_infers_package_name_from_folder(tmp_path):
    """If no package name is given, the folder name should be used as package."""
    pkg_dir = tmp_path / "inferredpkg"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").write_text("""# init""")
    (pkg_dir / "mod1.py").write_text("""HELLO = 'world'""")

    try:
        ModuleLoader.load_from_directory(str(pkg_dir))

        assert "inferredpkg.mod1" in sys.modules
        mod = sys.modules["inferredpkg.mod1"]
        assert mod.HELLO == "world"
    finally:
        _cleanup_module_names("inferredpkg.mod1", "inferredpkg")


def test_load_directory_ignores_non_python_files(tmp_path):
    """Loader must ignore non-Python files and import only *.py modules."""
    pkg_dir = tmp_path / "pkg2"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").write_text("""# init""")
    (pkg_dir / "good.py").write_text("""OK = True""")
    (pkg_dir / "ignored.txt").write_text("this is ignored")

    try:
        ModuleLoader.load_from_directory(str(pkg_dir))

        assert "pkg2.good" in sys.modules
        mod = sys.modules["pkg2.good"]
        assert mod.OK is True

        assert all("ignored" not in name for name in sys.modules.keys())
    finally:
        _cleanup_module_names("pkg2.good", "pkg2")
