from ..core.entity import Entity
from ..core.registry import register_entity


@register_entity('Tag')
class Tag(Entity):
    __entity_type__ = 'Tag'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
