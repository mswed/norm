import norm_the_orm as norm
from pprint import pprint


def test_simple_value():
    """
    Getting a text or int value from SG
    """

    shot = norm.Entity.from_id('Shot', 1251)
    pprint(shot)


test_simple_value()
