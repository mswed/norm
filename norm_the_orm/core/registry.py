class EntityRegistry:
    """
    Registry for entity types and their corresponding classes.
    This replaces the hardcoded MAPPER dictionary.
    """

    _registry = {}

    @classmethod
    def register(cls, entity_type, entity_class):
        """
        Register an entity class for a specific entity type

        :param entity_type: str, the ShotGrid entity type
        :param entity_class: class, the Entity subclass to use
        """
        cls._registry[entity_type] = entity_class
        # log.debug(f'Registered {entity_class.__name__} for entity type {entity_type}')

    @classmethod
    def get(cls, entity_type, default=None):
        """
        Get the registered entity class for a type

        :param entity_type: str, the ShotGrid entity type
        :param default: class, the default class to return if not found
        :return: class, the entity class to use
        """
        return cls._registry.get(entity_type, default)

    @classmethod
    def get_current_mappings(cls):
        """Return a dictionary of current entity mappings"""
        return {k: v.__name__ for k, v in EntityRegistry._registry.items()}


def register_entity(entity_type):
    def decorator(cls):
        EntityRegistry.register(entity_type, cls)
        return cls

    return decorator
