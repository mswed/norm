import pytest
from norm_the_orm import Task


def test_find_by_id(mock_session):
    """
    Search for a single item by ID
    """
    task = Task.query.by_id(657).all()
    assert len(task) == 1

    # What if we search for a none existing id?
    task = Task.query.by_id(-5).all()

    assert task is None
