# test dummies
from ..dummies.plugins.plugin_a import PluginA, PluginAConfig
from ..dummies.plugins.plugin_b import PluginB, PluginBConfig
from ..support.component_spec import ComponentSpec


def test_plugin_runs(make_components, context):
    plugins = make_components(
        ComponentSpec(
            component_cls=PluginA,
            config_cls=PluginAConfig,
            cfg=PluginAConfig(value=10, enabled=True),
        ),
        ComponentSpec(
            component_cls=PluginB,
            config_cls=PluginBConfig,
            cfg=PluginBConfig(enabled=True, flag=False),
        ),
        ctx=context,
    )

    for p in plugins:
        p.run()
    assert plugins[0].result == "A:10"
    assert plugins[1].result == "B:False"
