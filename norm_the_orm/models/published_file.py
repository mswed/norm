from ..core.entity import Entity
from ..core.registry import register_entity


@register_entity('PublishedFile')
class PublishedFile(Entity):
    __entity_type__ = 'PublishedFile'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
