from unittest import TestCase
from datetime import datetime
import norm_the_orm as norm
from shotgrid_flow import Flow


class TimeLogTests(TestCase):
    def setUp(self):
        self.session = norm.session.Session.new()

    def test_repeating_log(self):
        """
        Creating multiple time logs at once
        """

        logs = norm.TimeLog.repeating_log(
            'Production meeting', '2024-02-26', '10:30', '11:00', 142, 25877, repetitions=5
        )

        log_ids = [log.id.get() for log in logs]

        link = Flow.connect(user=True)

        filters = [['id', 'in', [*log_ids]]]
        fields = ['description', 'sg_start_time', 'sg_end_time', 'date']
        results = link.api.find('TimeLog', filters, fields)
        for r, log in zip(results, logs):
            self.assertEqual(datetime.strftime(r.get('sg_start_time'), '%H:%M'), log.start_time)
            self.assertEqual(datetime.strftime(r.get('sg_end_time'), '%H:%M'), log.end_time)
            self.assertEqual(r.get('date'), log.date.get())
            self.assertEqual(r.get('description'), log.description.get())
            # print('START TIME', datetime.strftime(r.get('sg_start_time'), '%H:%M'))
            # print('END TIME', datetime.strftime(r.get('sg_end_time'), '%H:%M'))
            # print('DATE', r.get('date'))
