from unittest import TestCase
import norm
from norm.flow import Flow


class ModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        norm.session.Session.new()

    def test_simple_value(self):
        """
        Getting a text or int value from SG
        """

        shot = norm.Entity.from_id("Shot", 1163)
        self.assertEqual(shot.bingo.get(), "HSM_SATL_0015")
        self.assertEqual(shot.sg_cut_in.get(), 1004)

    def test_entity_value(self):
        """
        Getting an entity back
        """

        shot = norm.Entity.from_id("Shot", 1163)
        created_by = shot.created_by

        # Check that we got an Entity back
        self.assertEqual(type(created_by), norm.Entity)

        # Check that we can get values from it
        self.assertEqual(created_by.email.get(), "support@shotgunsoftware.com")

    def test_multi_entity_value(self):
        """
        Getting a list of entities from a multi entity field
        """

        shot = norm.Entity.from_id("Shot", 1163)
        tasks = shot.tasks

        # check that we got entities
        self.assertTrue(all(isinstance(t, norm.Entity) for t in tasks.get()))

        # check that we can access them
        self.assertEqual(tasks.get()[0].bingo.get(), "Animation")

    def test_no_such_field(self):
        """
        What happens if we don't have this field?
        """
        shot = norm.Entity.from_id("Shot", 1163)
        with self.assertRaises(AttributeError):
            shot.bloop.get()

    def test_new_record(self):
        """
        Check that we can create empty records
        """
        shot = norm.Entity.new("Shot")
        # check that it's an ORM class
        self.assertTrue(isinstance(shot, norm.Entity))

        # confirm that it's empty
        self.assertEqual(shot.id.get(), "")

    def test_as_dict(self):
        """
        Check that entities return SG dicts when needed
        """
        # Create an empty shot and check that the project field is empty
        shot = norm.Entity.new("Shot")
        self.assertEqual(shot.project.get(), "")

        # Grab a project and assign it to the shot using the .as_dict() method
        project = norm.Entity.from_id("Project", 85)
        shot.project.set(project.as_dict())

        # Confirm that we successfully assigned the project
        self.assertEqual(shot.project.id.get(), 85)

    def test_new_record_sg(self):
        """
        Check we can create a new record in SG
        """
        # Create an empty shot and check that the project field is empty
        shot = norm.Entity.new("Shot")

        # Grab a project and assign it to the shot using the .as_dict() method
        project = norm.Entity.from_id("Project", 85)
        shot.project.set(project.as_dict())

        shot.code.set("This is a test shot")
        shot.description.set("A very important shot")

        s = norm.session.Session.current
        s.add(shot)
        s.commit()

        link = Flow.connect(user=True)
        results = link.api.find_one(
            shot.entity_type, [["id", "is", shot.id.get()]], ["code", "description"]
        )
        self.assertEqual(results.get("code"), "This is a test shot")
        self.assertEqual(results.get("description"), "A very important shot")
