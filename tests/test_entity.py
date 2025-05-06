import pytest
import norm_the_orm as norm


def test_simple_value(mock_session):
    """
    Getting a text or int value from SG
    """
    shot = norm.Entity.from_id(
        29338,
        'Shot',
    )
    assert shot.bingo.get() == 'ABC_030_010'
    assert shot.sg_head_in.get() == 1001


def test_multi_entity_value(mock_session):
    """
    Getting a list of entities from a multi entity field
    """

    shot = norm.Entity.from_id(29338, 'Shot')
    tasks = shot.tasks.get()

    # check that we got entities
    assert all(isinstance(t, norm.Entity) for t in tasks)

    # check that we can access them
    assert tasks[0].bingo.get() == 'anim'


def test_no_such_field(mock_session):
    """
    What happens if we don't have this field?
    """
    shot = norm.Entity.from_id(29338, 'Shot')
    with pytest.raises(AttributeError):
        shot.bloop.get()


def test_new_record(mock_session):
    """
    Check that we can create empty records
    """
    shot = norm.Entity.new('Shot')
    # check that it's an ORM class
    assert isinstance(shot, norm.Entity) is True

    # confirm that it's empty
    assert shot.id.get() == ''


def test_as_dict(mock_session):
    """
    Check that entities return SG dicts when needed
    """
    # Create an empty shot and check that the project field is empty
    shot = norm.Entity.new('Shot')
    assert shot.project.get() == ''

    # Grab a project and assign it to the shot using the .as_dict() method
    project = norm.Entity.from_id(101, 'Project')
    shot.project.set(project.as_dict())

    # Confirm that we successfully assigned the project
    assert shot.project.id.get() == 101


def test_new_record_sg(mock_session, mock_flow):
    """
    Check we can create a new record in SG
    """
    # Create an empty shot and check that the project field is empty
    shot = norm.Entity.new('Shot')

    # Grab a project and assign it to the shot using the .as_dict() method
    project = norm.Entity.from_id(101, 'Project')
    shot.project.set(project.as_dict())

    shot.code.set('This is a test shot')
    shot.description.set('A very important shot')

    s = norm.session.Session.current
    s.add(shot)
    s.commit()

    print('ABOUT TO SEARCH THE DB')
    results = mock_flow.api.find_one(
        shot.entity_type, [['id', 'is', shot.id.get()]], ['code', 'description']
    )
    print('RESULTS', results)
    assert results.get('code') == 'This is a test shot'
    assert results.get('description') == 'A very important shot'
