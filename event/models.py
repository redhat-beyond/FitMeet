from django.db import models
from category.models import Category
from location.models import Location
from poll.models import Poll


class Event(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True)
    poll = models.OneToOneField(Poll, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=40)
    max_participants = models.PositiveIntegerField()
    participants_num = models.PositiveIntegerField(default=1)
    start_time = models.DateTimeField("Event Starting Time")
    end_time = models.DateTimeField("Event End Time")
    is_private = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
