from collections import namedtuple
import logging
import os
from pprint import pprint
import time
from .exceptions import CommitError
from .utils import Logger
from shotgrid_flow import Flow


class Session:
    current = None

    @classmethod
    def new(cls):
        session = cls()
        cls.current = session
        return session

    def __init__(self):
        self.db = Flow.connect(user=True)
        self.schema = self.load_schema()

        logging.basicConfig(level=os.environ.get('LOGLEVEL', 'DEBUG'))
        self.log = Logger('Session')

        # We collect all entities created in the session, so we don't create them twice
        self.entities = []
        self.staged = set()

        if Session.current is None:
            Session.current = self

    def add(self, entity):
        """
        Stage an entity
        @param entity: Instance(Entity), entity to add to the staging area
        """

        self.staged.add(entity)

    def commit(self):
        """
        Update SG with our staging area
        """

        # data = {'code': 'Test shot',
        #         'project': {'id': 507,
        #                     'name': 'RND - Research and Development',
        #                     'type': 'Project'}}
        # record = self.db.api.create('Shot', data)
        # pprint(record)

        commited = set()
        for e in self.staged:
            try:
                fields = e.updated_fields()
                if not fields:
                    self.log.warning(f'Entity {e} has no updates')
                    # This entity was commited, but nothing was updated
                    return

                if e.is_synced:
                    # If id has been updated (can happen on new records) remove it from the updated fields
                    # since we can not update the id
                    if 'id' in fields.keys():
                        fields.pop('id')
                    # We are updating a record
                    sg_record = self.db.api.update(e.entity_type, e.id.get(), fields)
                else:
                    # We are creating a new record
                    # if e.is_project_bound:

                    # SG does not allow the creation of an empty record, so if we did not provide
                    # a name for the record, we set a generic name here
                    if not fields:
                        e.bingo.set(f'New {e.entity_type}')
                        fields = e.updated_fields()
                    sg_record = self.db.api.create(e.entity_type, fields)

                    # We grab the id and mark the entity as initialized
                    e.id.set(sg_record.get('id'))
                    e.initialized = True

                commited.add(e)

            except Exception as e:
                raise CommitError(f'Failed to commit {e}')

        self.staged = self.staged - commited
        if len(self.staged) > 0:
            print('Some entities failed to process!', self.staged)
            self.staged = set()
            # e.sync(sg_record)

    def get_entity_fields(self, entity_type):
        """
        Get only editable fields from SG
        @param entity_type:
        @return: dict{attrs: fields_attrs, names: field_names}, name and attributes for editable fields
        """
        fields_schema = self.schema.get(entity_type)
        field_names = [name for name in fields_schema]
        fields_data = namedtuple('FieldData', ['names', 'attrs'])

        return fields_data(field_names, fields_schema)

    def load_schema(self):
        schema = self.db.api.schema_read()
        return schema
