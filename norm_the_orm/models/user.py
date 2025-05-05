from ..core.entity import Entity
from ..core.registry import register_entity


@register_entity('User')
class User(Entity):
    __entity_type__ = 'User'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
