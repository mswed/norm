from ..core.entity import Entity
from ..core.registry import register_entity


@register_entity('Project')
class Project(Entity):
    __entity_type__ = 'Project'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
