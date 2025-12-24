import pytest
from pydantic import ValidationError

from opsflow.core.config import CoreConfig, NotifierConfig, PluginConfig

# product code
from opsflow.core.config.loader import ConfigLoader
from opsflow.core.notifier.registry import NotifierRegistry
from opsflow.core.plugin import PluginRegistry

from ..dummies.notifier.dummy_notifier import (
    DummyNotifier,
    DummyNotifierConfig,
)

# dummies (test-only components)
from ..dummies.plugins.plugin_a import PluginA, PluginAConfig
from ..dummies.plugins.plugin_b import PluginB, PluginBConfig


@pytest.fixture(autouse=True)
def register_components():
    """Reset registries and register dummy plugin/notifier types."""
    PluginRegistry.entries.clear()
    NotifierRegistry.entries.clear()

    PluginRegistry.register_class(PluginA, config=PluginAConfig)
    PluginRegistry.register_class(PluginB, config=PluginBConfig)
    NotifierRegistry.register_class(DummyNotifier, config=DummyNotifierConfig)

    yield

    PluginRegistry.entries.clear()
    NotifierRegistry.entries.clear()


def test_load_core_config_from_valid_yaml(tmp_path):
    """Valid YAML should load into CoreConfig with correct plugin/notifier configs."""
    p = tmp_path / "cfg.yaml"
    p.write_text(
        """
        logging:
          file: "test.log"
          debug: true

        dry_run: true

        plugins:
          plugin_a:
            enabled: true
            value: 5

        notifiers:
          dummy:
            enabled: true
            channel: "#ci"
        """
    )

    cfg = ConfigLoader.load(str(p))

    assert isinstance(cfg, CoreConfig)
    assert cfg.dry_run is True

    assert isinstance(cfg.plugins, dict)
    assert isinstance(cfg.plugins["plugin_a"], PluginConfig)
    assert cfg.plugins["plugin_a"].enabled is True

    assert isinstance(cfg.notifiers, dict)
    assert isinstance(cfg.notifiers["dummy"], NotifierConfig)
    assert cfg.notifiers["dummy"].enabled is True


def test_load_core_config_invalid_structure_raises(tmp_path):
    """Invalid YAML structure should raise a ValidationError."""
    p = tmp_path / "bad.yaml"
    p.write_text(
        """
        plugins:
          - "wrong"
        """
    )

    with pytest.raises(ValidationError):
        ConfigLoader.load(str(p))


def test_missing_plugin_and_notifier_sections_defaults_to_none(tmp_path):
    """If plugins/notifiers are missing in YAML, CoreConfig fields should be None."""
    p = tmp_path / "minimal.yaml"
    p.write_text(
        """
        logging:
          file: "logs.txt"
        """
    )

    cfg = ConfigLoader.load(str(p))

    assert cfg.plugins == {}
    assert cfg.notifiers == {}


def test_extra_fields_in_yaml_are_ignored(tmp_path):
    """Extra fields in config entries must be ignored by pydantic."""
    p = tmp_path / "extra.yaml"
    p.write_text(
        """
        plugins:
          plugin_a:
            enabled: true
            extra_field: "ignored"
        """
    )

    cfg = ConfigLoader.load(str(p))
    plugin_cfg = cfg.plugins["plugin_a"]

    assert plugin_cfg.enabled is True
    assert not hasattr(plugin_cfg, "extra_field")


def test_specific_config_models_are_instantiated(tmp_path):
    """Plugin/notifier configs must use their specific subclass models."""
    p = tmp_path / "specific.yaml"
    p.write_text(
        """
        plugins:
          plugin_a:
            enabled: true
            value: 7
          plugin_b:
            enabled: true
            flag: false

        notifiers:
          dummy:
            enabled: true
            channel: "#ops"
        """
    )

    cfg = ConfigLoader.load(str(p))

    assert isinstance(cfg.plugins["plugin_a"], PluginAConfig)
    assert cfg.plugins["plugin_a"].value == 7

    assert isinstance(cfg.plugins["plugin_b"], PluginBConfig)
    assert cfg.plugins["plugin_b"].flag is False

    assert isinstance(cfg.notifiers["dummy"], DummyNotifierConfig)
    assert cfg.notifiers["dummy"].channel == "#ops"


def test_subclass_validation_fails_on_incorrect_field_type(tmp_path):
    """Wrong field type inside a plugin config should raise ValidationError."""
    p = tmp_path / "bad_type.yaml"
    p.write_text(
        """
        plugins:
          plugin_a:
            enabled: true
            value: "bad-type"
        """
    )

    with pytest.raises(ValidationError):
        ConfigLoader.load(str(p))
