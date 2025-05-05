from ..core.registry import EntityRegistry
from ..core.entity import Entity, Field
from .asset import Asset
from .shot import Shot
from .step import Step
from .task import Task
from .project import Project
from .version import Version
from .timelog import TimeLog


# Register default mappings
def register_defaults():
    EntityRegistry.register('Asset', Asset)
    EntityRegistry.register('Shot', Shot)
    EntityRegistry.register('Step', Step)
    EntityRegistry.register('Task', Task)
    EntityRegistry.register('Project', Project)
    EntityRegistry.register('TimeLog', TimeLog)
    EntityRegistry.register('Version', Version)


# Initialize the registry
register_defaults()

# Export everything needed
__all__ = [
    'Entity',
    'Field',
    'EntityRegistry',
    'Shot',
    'Task',
    'Project',
    'Version',
    'TimeLog',
]
