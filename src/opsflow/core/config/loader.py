import yaml

from ..notifier import NotifierRegistry
from ..plugin import PluginRegistry
from ..registry.entry import RegistryEntry
from .schema import CoreConfig


class ConfigLoader:
    """Load and validate the application configuration from YAML.

    Parses the YAML file, validates the CoreConfig, and creates configuration
    objects for plugins and notifiers using their registries.
    """

    @staticmethod
    def load(path: str) -> CoreConfig:
        """Load and validate the CoreConfig from a YAML file.

        Args:
            path (str): Path to the YAML configuration file.

        Returns:
            CoreConfig: Validated CoreConfig including plugin and notifier
                configuration objects.

        Raises:
            OSError: If the configuration file cannot be read.
            ValidationError: If the YAML content is invalid.
            ValueError: If an unknown plugin or notifier is referenced.
        """
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        # Validate top-level CoreConfig
        core = CoreConfig.model_validate(raw)

        # Load plugins and notifiers using the same helper method
        core.plugins = ConfigLoader._load_entries(raw.get("plugins"), PluginRegistry.entries)
        core.notifiers = ConfigLoader._load_entries(raw.get("notifiers"), NotifierRegistry.entries)

        return core

    @staticmethod
    def _load_entries(entry_data: dict | None, entries: dict[str, RegistryEntry]) -> dict:
        """Create validated configuration objects from registry definitions.

        Maps raw YAML configuration data to validated configuration model
        instances defined by the registry.

        Args:
            entry_data (Optional[dict]): Mapping of entry names to raw YAML data.
            entries (dict[str, RegistryEntry]): Registry providing config models.

        Returns:
            dict: Mapping of entry names to validated configuration objects.
                Returns an empty dict if no entries are defined.

        Raises:
            ValueError: If an entry name is not registered.
            ValidationError: If a configuration model fails validation.
        """
        if not entry_data:
            return {}

        result = {}
        for name, raw_cfg in entry_data.items():
            entry = entries.get(name)
            if entry is None:
                raise ValueError(f"Unknown entry: {name}")

            config_cls = entry.config_cls
            result[name] = config_cls.model_validate(raw_cfg)

        return result
