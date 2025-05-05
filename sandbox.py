from norm_the_orm import Entity, EntityRegistry
from pprint import pprint


def test_simple_value():
    """
    Getting a text or int value from SG
    """

    shot = Entity.from_id('Shot', 1251)
    pprint(shot)


pprint(EntityRegistry.get_current_mappings())
test_simple_value()
