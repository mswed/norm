from ..core.entity import Entity
from ..core.registry import register_entity


@register_entity('Shot')
class Shot(Entity):
    __entity_type__ = 'Shot'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
