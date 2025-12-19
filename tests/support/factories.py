from typing import Optional
from opsflow.core.factory.base import Factory
from opsflow.core.models.context import Context
from opsflow.core.registry.base import Registry
from opsflow.core.registry.entry import RegistryEntry

from .component_spec import ComponentSpec

TestRegistry = Registry(default_config=dict, base_cls=object, kind="Test")


def make_components_factory(logger):
    def _make(*specs: ComponentSpec, ctx: Optional[Context] = None):
        TestRegistry.entries.clear()

        components_cfg = {}

        for spec in specs:
            name = spec.name or spec.component_cls.name

            TestRegistry.entries[name] = RegistryEntry(
                component_cls=spec.component_cls,
                config_cls=spec.config_cls,
            )
            components_cfg[name] = spec.cfg

        factory = Factory(
            registry=TestRegistry,
            components_cfg=components_cfg,
            logger=logger,
            ctx=ctx,
        )

        return list(factory.create_all())

    return _make
