from unittest import TestCase
from norm_the_orm import Session, Shot, Task, Entity, Project


class SearchTests(TestCase):
    def setUp(self):
        self.session = Session.new()

    def test_find_by_id(self):
        """
        Search for a single item by id
        """
        task = Task.query.by_id(147514).all()
        self.assertEqual(len(task), 1)

        # What if we search for a none existing id?
        task = Task.query.by_id(-5).all()
        self.assertIsNone(task)

    def test_find_by_ids(self):
        """
        Search for multiple items by id
        """

        tasks = Task.query.by_ids([147425, 147513, 147514, 147679, 147680]).all()
        self.assertEqual(len(tasks), 5)
        self.assertEqual(tasks[0].bingo.get(), 'Camera Track')

    def test_find_by_name(self):
        """
        Search for an entity by name
        """

        # Strict search returns only names that match the search term exactly
        tasks = Shot.query.by_name('RND_OUT_006_020', strict=True).all()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].bingo.get(), 'RND_OUT_006_020')

        # Strict search returns names contain the search term
        tasks = Shot.query.by_name('RND').all()
        self.assertGreaterEqual(len(tasks), 40)

    def test_find_one(self):
        """
        Search for an entity by name returning only one record
        """

        # Strict search returns names contain the search term
        tasks = Shot.query.by_name('RND').all()
        self.assertGreaterEqual(len(tasks), 1)


class SessionTests(TestCase):
    def setUp(self):
        self.session = Session.new()

    def test_create_record(self):
        project = Project.query.by_name('RND').one()
        print(project)
        shot = Entity.new('Shot')
        shot.bingo.set('NORM TEST SHOT')
        shot.project.set(project.as_dict())

        self.session.add(shot)
        self.session.commit()

        created_shot = Shot.query.by_id(shot.id.get()).one()
        self.assertEqual(created_shot.bingo.get(), 'NORM TEST SHOT')
        print('Created new record')

    def test_delete_record(self):
        shot = Shot.query.by_name('NORM TEST SHOT').delete()
        self.assertIsInstance(shot, dict)
        self.assertIn('DELETED', shot)
        self.assertIsInstance(shot['DELETED'], int)
