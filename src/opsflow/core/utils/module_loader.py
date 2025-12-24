import importlib
import pathlib
import sys


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
        if not package:
            package = directory.name

        parent_dir = str(directory.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        try:
            for file in directory.glob("*.py"):
                if file.name == "__init__.py":
                    continue
                module_name = file.stem
                importlib.import_module(f"{package}.{module_name}")
        finally:
            if parent_dir in sys.path:
                sys.path.remove(parent_dir)
