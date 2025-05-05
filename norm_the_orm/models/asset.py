from ..core.entity import Entity
from ..core.registry import register_entity


@register_entity('Asset')
class Asset(Entity):
    __entity_type__ = 'Asset'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
