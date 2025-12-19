import pytest

from ..dummies.plugins.plugin_a import PluginA, PluginAConfig
from ..support.component_spec import ComponentSpec


@pytest.fixture
def plugin_a(make_components, context, request):
    param = getattr(request, "param", {})
    return make_components(
        ComponentSpec(
            name="plugin_a",
            component_cls=PluginA,
            config_cls=PluginAConfig,
            cfg=PluginAConfig(enabled=param.get("enabled", True)),
        ),
        ctx=context,
    )


def test_creates_enabled_component(plugin_a):
    assert len(plugin_a) == 1
    comp = plugin_a[0]
    assert isinstance(comp, PluginA)
    assert isinstance(comp.config, PluginAConfig)


@pytest.mark.parametrize("plugin_a", [{"enabled": False}], indirect=True)
def test_disabled_component_is_skipped(plugin_a):
    assert plugin_a == []
