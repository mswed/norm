from unittest import TestCase
from norm import Session, Shot, Task, Entity, Project


class SearchTests(TestCase):
    def setUp(self):
        self.session = Session.new()

    def test_find_by_id(self):
        """
        Search for a single item by id
        """
        task = Task.query.by_id(5654).all()
        self.assertEqual(len(task), 1)

        # What if we search for a none existing id?
        task = Task.query.by_id(-5).all()
        self.assertIsNone(task)

    def test_find_by_ids(self):
        """
        Search for multiple items by id
        """

        tasks = Task.query.by_ids([5653, 5654, 5651, 5655, 5652]).all()
        self.assertEqual(len(tasks), 5)
        self.assertEqual(tasks[0].bingo.get(), "Comp")

    def test_find_by_name(self):
        """
        Search for an entity by name
        """

        # Strict search returns only names that match the search term exactly
        shots = Shot.query.by_name("HSM_SATL_0060", strict=True).all()
        self.assertEqual(len(shots), 1)
        self.assertEqual(shots[0].bingo.get(), "HSM_SATL_0060")

        # Broad search returns names contain the search term
        shots = Shot.query.by_name("HSM").all()
        self.assertGreaterEqual(len(shots), 7)

    def test_find_one(self):
        """
        Search for an entity by name returning only one record
        """

        # Strict search returns names contain the search term
        shot = Shot.query.by_name("HSM").one()
        self.assertIsInstance(shot, Shot)


class SessionTests(TestCase):
    def setUp(self):
        self.session = Session.new()

    def test_create_record(self):
        project = Project.query.by_name("Demo: Animation with Cuts").one()
        shot = Entity.new("Shot")
        shot.bingo.set("NORM TEST SHOT")
        shot.project.set(project.as_dict())

        self.session.add(shot)
        self.session.commit()

        created_shot = Shot.query.by_id(shot.id.get()).one()
        self.assertEqual(created_shot.bingo.get(), "NORM TEST SHOT")

    def test_delete_record(self):
        shot = Shot.query.by_name("NORM TEST SHOT").delete()
        self.assertIsInstance(shot, dict)
        self.assertIn("DELETED", shot)
        self.assertIsInstance(shot["DELETED"], int)
