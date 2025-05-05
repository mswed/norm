from datetime import date, datetime, timedelta

from .project import Project
from .task import Task
from ..core.entity import Entity
from ..core.registry import register_entity
from ..exceptions import NormException
from ..session import Session


@register_entity('TimeLog')
class TimeLog(Entity):
    __entity_type__ = 'TimeLog'

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
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if repetitions is not None:
            end_date = start_date + timedelta(days=repetitions)
        elif end_date is not None:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            raise NormException('Please provide an end date or number of repetitions!')

        project = Project.from_id('Project', project_id)
        task = Task.from_id('Task', task_id)

        logs = []
        for day in cls.date_range(start_date, end_date):
            time_log = cls.new()
            time_log.description.set(description)
            time_log.project.set(project.as_dict())
            time_log.entity.set(task.as_dict())

            real_start_time = datetime.strptime(start_time, '%H:%M')
            real_end_time = datetime.strptime(end_time, '%H:%M')
            time_log.sg_start_time.set(
                day.replace(hour=real_start_time.hour, minute=real_start_time.minute)
            )
            time_log.sg_end_time.set(
                day.replace(hour=real_end_time.hour, minute=real_end_time.minute)
            )
            time_log.duration.set(
                (time_log.sg_end_time.get() - time_log.sg_start_time.get()).total_seconds() / 60
            )
            time_log.date.set(day.strftime('%Y-%m-%d'))
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
        return datetime.strftime(self.sg_start_time.get(), '%H:%M')

    @property
    def end_time(self):
        return datetime.strftime(self.sg_end_time.get(), '%H:%M')
