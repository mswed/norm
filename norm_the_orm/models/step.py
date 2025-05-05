from ..core.entity import Entity
from ..core.registry import register_entity


@register_entity('Step')
class Step(Entity):
    __entity_type__ = 'Step'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
