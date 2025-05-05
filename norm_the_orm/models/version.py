from ..core.entity import Entity
from ..core.registry import register_entity


@register_entity('Version')
class Version(Entity):
    __entity_type__ = 'Version'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
