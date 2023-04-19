from django.db import models
from datetime import timedelta, datetime


def get_default_end_date():
    return datetime.now() + timedelta(days=1)


class Poll(models.Model):
    event_id = models.OneToOneField(to='event.Event', on_delete=models.CASCADE,
                                    related_name='poll_ref', null=True)
    max_suggestions = models.PositiveIntegerField()
    end_time = models.DateTimeField(default=get_default_end_date)
