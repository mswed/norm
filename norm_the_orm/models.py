import datetime
import os
import logging
from pprint import pprint
from datetime import date, datetime, timedelta

from .session import Session
from . import search
from .exceptions import NormException

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)


class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class Entity:
    update = False
    __entity_type__ = None
    __nameoverride__ = None

    @classmethod
    def get_query(cls):
        return search.Query(cls())

    # This magic is a way to define class properties as described here:
    # https://stackoverflow.com/a/1383402
    query = classproperty(get_query)

    @classmethod
    def empty(cls, entity_type):
        # Get all the fields data
        fields_info = Session.current.get_entity_fields(entity_type)

        return cls(entity_type, fields_info.attrs, data={})

    @classmethod
    def from_id(cls, entity_type, entity_id):
        """
        Create an Entity from an SG Entity ID
        @param entity_type: str, type of entity to create
        @param entity_id: int, SG entity ID
        @return: Instance(Entity), a class representing the SG entity
        """

        log.debug(f"Creating record from ID {entity_type}, {entity_id}")

        if Session.current is None:
            Session.new()

        # Get all the fields data
        fields_info = Session.current.get_entity_fields(entity_type)

        # Query SG
        fields = fields_info.names
        filters = [["id", "is", entity_id]]
        results = Session.current.db.api.find_one(entity_type, filters, fields)
        log.debug(f"Found records on ShotGrid {results}")
        entity = MAPPER.get(entity_type, cls)
        # if entity:
        #     log.debug('Creating entity of type', entity)
        return entity(entity_type, fields_info.attrs, results)

    @classmethod
    def new(cls, entity_type=None, data=None):
        """
        Create a new SG record
        @param entity_type: str, type of entity to create
        @param data: dict{field_name, value}, a dictionary containing sg data (usually from a sg query)
        @return: Instance(Entity), python class representing the new record
        """
        if entity_type is None:
            if cls.__entity_type__ is not None:
                entity_type = cls.__entity_type__
            else:
                raise NormException("No entity type provided")

        fields_info = Session.current.get_entity_fields(entity_type)

        if data is None:
            data = {}
        return cls(entity_type, fields_info.attrs, data=data)

    def __init__(self, entity_type=None, fields=None, data=None):
        """
        Create an entity class
        @param entity_type: str, type of entity to create (Shot, Task, TimeLog, etc.)
        @param fields: dict{field_name, dict{field_info}}, a dictionary containing field names and info
        @param data: dict{field_name, value}, a dictionary containing sg data (usually from a sg query)
        """

        self._entity_type = entity_type
        self.fields = (
            self.session.get_entity_fields(self.entity_type).attrs
            if fields is None
            else fields
        )

        self.initialized = False
        self.changed = False

        if data is None:
            data = {}

        self.sync(data)
        self.nameo = self.bingo
        # self.query = search.Query(self)

        # Add the instance to the instance list. This will be used by the expand method
        Session.current.entities.append(self)

    def __getattribute__(self, item):
        """
        Override the class's get attribute function, so we can return a Field class instead
        @param item: str, attribute to get
        @return:
        """
        # log.debug(f'ITEM TYPE IS {type(item)}')

        # Check if we have the attribute
        try:
            obj = object.__getattribute__(self, item)
        except AttributeError:
            # We did not find the attribute
            if not (item.startswith("__") and item.endswith("__")):
                # If we didn't look for a builtin attr alert the user it was not found
                raise AttributeError(
                    f"{self.entity_type} does not have the attribute {item}"
                )
            # And exit
            return

        if hasattr(obj, "__get__"):
            # We have a Field instance use its get function
            # log.debug(f'Got a field attribute {item}')
            return obj.__get__(self, self)

        # This is a regular attribute, just return it
        return obj

    def __repr__(self):
        shot_name = False
        try:
            shot_name = self.bingo.get()
        except AttributeError:
            pass

        if not shot_name:
            shot_name = "Uninitialized"

        if self.__nameoverride__ is None:
            return f"<{self.entity_type.title()}: {shot_name}>"
        else:
            return f"<{self.__nameoverride__.title()} ({self.__nameoverride__}): {shot_name}>"

    @property
    def bingo(self):
        """
        And bingo was his name-o. Return the record name.
         In SG different entities use different fields to store the name, so we need to pick the correct one
        @return: str, name of record or None if no name is defined
        """

        if hasattr(self, "name"):
            return getattr(self, "name")

        if hasattr(self, "code"):
            return getattr(self, "code")

        if hasattr(self, "content"):
            return getattr(self, "content")

        if hasattr(self, "title"):
            return getattr(self, "title")

        if hasattr(self, "description"):
            return getattr(self, "description")

        return None

    @property
    def entity_type(self):
        # WE did not provide an entity type try to get it from the class
        if self._entity_type is None:
            self._entity_type = self.__class__.__entity_type__
        if not self._entity_type:
            raise NormException(
                "You must specify an entity type when creating an entity class. Either by using "
                'a subclass like Shot, or manually like Entity("shot") '
            )
        return self._entity_type

    @property
    def is_synced(self):
        return self.id.get() != ""

    @property
    def is_project_bound(self):
        """
        SG entities can be bound to a project or not. Right now we can only handle project bound entities.
        @return: bool, do we have a project assigned to the entity?
        """
        try:
            return isinstance(self.project.get(), Entity)
        except AttributeError:
            return False

    @property
    def log(self):
        return self.session.log

    @property
    def session(self):
        if Session.current is None:
            session = Session()

        return Session.current

    def as_dict(self):
        """
        Get the entity as a SG dictionary
        @return: dict{type: entity_type, id: entity_id, name: entity_name}
        """

        return {"type": self.entity_type, "id": self.id.get(), "name": self.bingo.get()}

    @property
    def entity_fields(self):
        """
        Return all available entity fields
        @return: list(str), list of available fields
        """
        f = [x for x in dir(self) if not x.startswith("__")]

        return f

    @property
    def upper_class(self):
        """
        Get the creating class (useful for class variable access)
        @return: class, name of parent class
        """
        return self.__class__

    def sync(self, data):
        """
        Sync the object with SG
        """

        # create fields based on the information found in the fields variable, and assign it the data
        # found in the data variable. Note that the field variable has both the name of the field
        # and its settings (such as if it's editable)

        if self.initialized:
            # We are updating the entity we first need to switch to update mode so the Fields will return themselves
            # instead of the Entities they store
            self.upper_class.update = True
            for f, v in self.fields.items():
                # Grab the attribute
                field = getattr(self, f)
                if isinstance(field, Field):
                    # The attribute is a Field
                    if data.get(f) is not None:
                        # We got an update from SG update the field
                        field.set(data.get(f))
                        # Set its status to unchanged
                        field.changed = False

            self.upper_class.update = False
        else:
            for f, v in self.fields.items():
                # log.debug(f'Creating attr {f} with value {data.get(f, "")} and type {v["data_type"]}')
                try:
                    setattr(
                        self,
                        f,
                        Field(
                            name=f,
                            value=data.get(f, ""),
                            sg_name=v["name"]["value"],
                            editable=v["editable"]["value"],
                            data_type=v["data_type"]["value"],
                            entity=self,
                        ),
                    )
                except AttributeError as e:

                    continue
            self.initialized = True

    def updated_fields(self):
        """
        Get all the fields that were updated in a format that SG understands
        @return:
        """
        updated_fields = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Field) and v.changed:
                if v.is_multi_entity:
                    updated_fields[v.name] = [
                        e.get().as_dict() if isinstance(e, Entity) else e
                        for e in v.get()
                    ]
                else:
                    updated_fields[v.name] = (
                        v.get().as_dict() if isinstance(v.get(), Entity) else v.get()
                    )

        return updated_fields

    def get(self):
        msg = (
            f"{self.bingo.get()} is an entity of type {self.entity_type} you can not run .get() directly on it. "
            f"You can, however, access its attributes by doing something like Entity.bingo.get()"
        )

        self.log.info(msg)

        return self


class Field:
    """
    A descriptor to get and set SG fields
    """

    def __init__(
        self,
        name,
        value=None,
        editable=False,
        data_type=None,
        entity=None,
        sg_name=None,
    ):
        """
        An SG field
        @param name: str, name of field
        @param value: str, value of field
        @param editable: bool, is this field editable or not?
        @param data_type: str, type of field
        """

        self.name = name
        self.value = value
        self.editable = editable
        self.data_type = data_type
        self.entity = entity
        self.sg_name = sg_name

        self.changed = False
        # log.debug(f'Created FIELD {self.name} with value {self.value} and type {self.data_type}')

    def __eq__(self, other):
        if self.data_type == "entity":
            return [self.name, "is", {"type": self.sg_name, "id": other}]

        return [self.name, "is", other]

    def __get__(self, instance, owner):
        """
        Override the class's __get__ function so we can return info from the field
        @param instance: instance(Entity), the entity calling the field
        @param owner:  instance(Entity), the entity calling the field #TODO: how is that different from instance?
        @return: dynamic?
        """

        if self.value == "":
            self.log.debug("Value is empty, returning the Field object")
            return self

        if Entity.update:
            self.log.debug("Updating record, returning the Field object")
            return self

        if self.is_entity and self.is_orm:
            self.log.debug("Value is already an ORM will return value")
            pass

        elif self.is_entity and not self.is_orm:
            self.log.debug(f"{self} contains an entity should return it")
            # We have an entity that has not yet been converted to an orm object. Convert and return.
            self.value = self.value_to_orm(self.value)

        elif self.is_multi_entity:
            self.log.debug(f"{self} contains multi-entities should return a list")
            # we have a multi entity check if they were all converted
            if not all(isinstance(e, Entity) for e in self.value):
                # not all values are Entities
                self.value = [
                    self.value_to_orm(e) if isinstance(e, dict) else e
                    for e in self.value
                ]
            return self

        else:
            # self.log.debug(f'Value is text or number, returning {self.value}')
            # This is just a normal value, return the instance so we can run get() or any other method on it
            return self

        self.log.debug(f"Finished Field processing returning value {self.value}")
        return self.value

    def __ne__(self, other):
        if self.data_type == "entity":
            return [self.name, "is_not", {"type": self.sg_name, "id": other}]

        return [self.name, "is_not", other]

    def __repr__(self):
        return f"<Field: {self.name} {self.data_type} {self.value}>"

    def __rshift__(self, other):
        return [self.name, "contains", other]

    @property
    def is_orm(self):
        """
        Check if the value of the field has already been converted to an Entity object
        @return: bool, is the value an entity object?
        """
        return isinstance(self.value, Entity)

    @property
    def is_entity(self):
        """
        Check if the SG field stores a single entity
        @return: bool, does the value represent an entity?
        """
        return self.data_type == "entity"

    @property
    def is_multi_entity(self):
        return self.data_type == "multi_entity"

    @property
    def log(self):
        return self.entity.log

    def get(self, as_dict=False):
        if isinstance(self.value, Entity):
            self.entity.log.debug(
                f"{self.name} contains an entity to access it do something like {self.name}.bingo.get()"
            )

        # Regular return
        return self.value

    def set(self, value):
        original_value = self.value
        self.value = None if value == "" else value

        if original_value != self.value:
            # Mark the field as changed
            self.changed = True

            # mark the record as changed
            self.entity.changed = True

    def value_to_orm(self, value: dict):
        """
        Convert an entity from SG into an Entity object
        @return: Instance(Entity), a python representation of an SG entity
        """
        self.entity.log.debug(f"VALUE TO ORM: Converting {self} to an Entity")
        if self.value:
            log.debug(f"Value to convert is {value}")
            try:
                # Search our entities list to see if we already converted this entity before
                entity = [
                    e
                    for e in Session.current.entities
                    if e.id.get() == value.get("id")
                    and e.entity_type == value.get("type")
                ][0]
                self.entity.log.debug(
                    f"No need to convert, we already converted before: {entity}"
                )
            except IndexError:
                # We did not find an entity object, convert the value
                entity = Entity.from_id(value.get("type"), value.get("id"))
                self.entity.log.debug("We converted based on the id")
            except AttributeError:
                self.entity.log.debug("Failed to convert")
                raise AttributeError(
                    f"Could not get field value for  {self.entity.bingo.get()} {self.name}"
                )

            return entity


class Asset(Entity):
    __entity_type__ = "Asset"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BidLine(Entity):
    __entity_type__ = "CustomNonProjectEntity09"
    __nameoverride__ = "BidLine"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BidParam(Entity):
    __entity_type__ = "CustomNonProjectEntity08"
    __nameoverride__ = "BidParam"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Camera(Entity):
    __entity_type__ = "CustomNonProjectEntity03"
    __nameoverride__ = "Camera"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.bingo.get()}  ({self.sg_plate_width.get()} x {self.sg_plate_height.get()})"


class Project(Entity):
    __entity_type__ = "Project"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PublishedFile(Entity):
    __entity_type__ = "PublishedFile"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Shot(Entity):
    __entity_type__ = "Shot"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Step(Entity):
    __entity_type__ = "Step"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Tag(Entity):
    __entity_type__ = "Tag"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Task(Entity):
    __entity_type__ = "Task"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TimeLog(Entity):
    __entity_type__ = "TimeLog"

    @classmethod
    def repeating_log(
        cls,
        description,
        start_date,
        start_time,
        end_time,
        project_id,
        task_id,
        repetitions=None,
        end_date=None,
    ):

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if repetitions is not None:
            end_date = start_date + timedelta(days=repetitions)
        elif end_date is not None:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            raise NormException("Please provide an end date or number of repetitions!")

        project = Entity.from_id("Project", project_id)
        task = Entity.from_id("Task", task_id)

        logs = []
        for day in cls.date_range(start_date, end_date):
            time_log = cls.new()
            time_log.description.set(description)
            time_log.project.set(project.as_dict())
            time_log.entity.set(task.as_dict())

            real_start_time = datetime.strptime(start_time, "%H:%M")
            real_end_time = datetime.strptime(end_time, "%H:%M")
            time_log.sg_start_time.set(
                day.replace(hour=real_start_time.hour, minute=real_start_time.minute)
            )
            time_log.sg_end_time.set(
                day.replace(hour=real_end_time.hour, minute=real_end_time.minute)
            )
            time_log.duration.set(
                (
                    time_log.sg_end_time.get() - time_log.sg_start_time.get()
                ).total_seconds()
                / 60
            )
            time_log.date.set(day.strftime("%Y-%m-%d"))
            logs.append(time_log)

            Session.current.add(time_log)
            Session.current.commit()

        return logs

    @classmethod
    def date_range(cls, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def start_time(self):
        return datetime.strftime(self.sg_start_time.get(), "%H:%M")

    @property
    def end_time(self):
        return datetime.strftime(self.sg_end_time.get(), "%H:%M")


class User(Entity):
    __entity_type__ = "HumanUser"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Version(Entity):
    __entity_type__ = "Version"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


MAPPER = {
    "Shot": Shot,
    "Step": Step,
    "Task": Task,
    "Project": Project,
    "TimeLog": TimeLog,
    "Version": Version,
    "CustomNonProjectEntity03": Camera,
    "CustomNonProjectEntity09": BidLine,
    "CustomNonProjectEntity08": BidParam,
}
