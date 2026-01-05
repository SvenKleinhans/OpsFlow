import importlib
import pathlib
import sys
import types


class ModuleLoader:
    """Utility class to dynamically load Python modules from directories."""

    @staticmethod
    def load_from_directory(path: str, package: str | None = None) -> None:
        """
        Import all Python modules from the given directory.

        Args:
            path (str): Filesystem path (relative or absolute) to the directory.
            package (Optional[str]): Python package prefix. Defaults to folder name.

        Raises:
            ImportError: If a module fails to import.
        """
        directory = pathlib.Path(path).resolve()

        runtime_root = "__opsflow_runtime__"
        runtime_ns = f"{runtime_root}.{hash(directory)}"

        if runtime_root not in sys.modules:
            root_pkg = types.ModuleType(runtime_root)
            root_pkg.__path__ = []
            sys.modules[runtime_root] = root_pkg

        if runtime_ns not in sys.modules:
            pkg = types.ModuleType(runtime_ns)
            pkg.__path__ = [str(directory)]
            sys.modules[runtime_ns] = pkg

        parent_dir = str(directory.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        try:
            for file in directory.glob("*.py"):
                if file.name == "__init__.py":
                    continue

                full_name = f"{runtime_ns}.{file.stem}"
                if full_name in sys.modules:
                    continue

                importlib.import_module(full_name)
        finally:
            if parent_dir in sys.path:
                sys.path.remove(parent_dir)
