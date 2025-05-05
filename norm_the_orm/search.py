from pprint import pprint

from .session import Session


class Query:
    def __init__(self, entity):
        self.entity = entity
        self.filters = []
        self.search_fields = []
        self.results = []

    @property
    def valid_results(self):
        """
        Results are not empty and are a dictionary
        @return: bool, are the results valid?
        """
        if len(self.results) > 0:
            try:
                return type(self.results[0]) is dict
            except IndexError:
                pass

        return False

    @property
    def session(self):
        if Session.current is None:
            Session()

        return Session.current

    def all(self, orm=True):
        """
        Return all found records
        @param orm: bool, returns orm objects if true and a dictionary if False
        @return: list([norm, ...])
        """
        self.find()

        if self.valid_results:
            if orm:
                entities = []
                for record in self.results:
                    record_as_entity = self.entity.new(self.entity.entity_type, record)
                    entities.append(record_as_entity)
                return entities
            else:
                return self.results

    def one(self):
        """
        Find a single record and return it.
        @return: norm
        """
        fields = self.entity.entity_fields
        self.results = self.session.db.api.find_one(
            self.entity.entity_type, self.filters, fields
        )

        return self.entity.new(self.entity.entity_type, self.results)

    def delete(self):
        """
        Find a single record and delete it.
        @return: norm
        """
        results = self.session.db.api.find_one(self.entity.entity_type, self.filters)

        if results:
            deleted = self.session.db.api.delete(
                self.entity.entity_type, results.get("id")
            )
            if deleted:
                return {"DELETED": results.get("id")}

        return {"error": "Failed to delete record"}

    def by_id(self, entity_id):
        self.filters.append(["id", "is", entity_id])

        return self

    def by_ids(self, entity_ids: list):
        self.filters.append(["id", "in", [*entity_ids]])
        return self

    def by_name(self, name, strict=False):
        # Query SG
        fields = self.entity.entity_fields
        name_field = self.entity.nameo.name

        if strict:
            self.filters.append([f"{name_field}", "is", name])
        else:
            self.filters.append([f"{name_field}", "contains", name])

        return self

    def fields(self, fields):
        self.search_fields = fields
        return self

    def filter_by(self, *args):
        for a in args:
            self.filters.append(a)
        return self

    def find(self):
        fields = self.search_fields if self.search_fields else self.entity.entity_fields

        self.results = self.session.db.api.find(
            self.entity.entity_type, self.filters, fields
        )
