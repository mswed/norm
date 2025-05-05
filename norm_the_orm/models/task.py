from ..core.entity import Entity
from ..core.registry import register_entity


@register_entity('Task')
class Task(Entity):
    __entity_type__ = 'Task'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
