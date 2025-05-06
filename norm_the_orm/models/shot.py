from typing import List, Optional
from ..core.entity import Entity
from ..core.registry import register_entity


@register_entity('Shot')
class Shot(Entity):
    __entity_type__ = 'Shot'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_tasks_from_step(self, step) -> Optional[List]:
        """
        Get all tasks from a specific pipeline step
        """
        tasks = self.tasks.get()

        filtered_tasks = [t for t in tasks if t.step and t.step.bingo.get().lower() == step.lower()]

        return filtered_tasks
