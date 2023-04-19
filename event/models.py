from django.db import models
from category.models import Category
from location.models import Location
from category_location.models import CategoryLocation
from poll.models import Poll
from users.models import Profile
from teams.models import Teams
from django.core.exceptions import ValidationError
import pytz


class EvnetManager(models.Manager):
    invalid_category_location_message = (
        "The pair of category and location is not in category location table"
    )
    invalid_time_error_message = "Error - event end time cannot be equal or less than start time"
    invalid_poll_error = "Error- poll end time is late than the event start time"

    def __str__(self) -> str:
        return self.name

    def create_event(
        self,
        category_id,
        location_id,
        name,
        max_participants,
        start_time,
        end_time,
        is_private,
        poll_id,
    ):
        # Check if category and location are valid
        self.throw_exception_if_invalid_category_location(
            category_id=category_id, location_id=location_id
        )
        my_event_catrgoty = Category.objects.get(id=category_id)
        my_event_location = Location.objects.get(id=location_id)

        # Check start_time and time
        self.throw_exception_if_invalid_date(start_time=start_time, end_time=end_time)

        # validate poll
        my_poll = Poll.objects.get(id=poll_id)
        self.throw_exception_if_invalid_poll_end_time(
            poll_end_time=my_poll.end_time, event_start_time=start_time
        )

        # Update user event table
        # Todo - update user event table when it's created
        # save event
        my_event = Event(
            category=my_event_catrgoty,
            location=my_event_location,
            poll=my_poll,
            name=name,
            max_participants=max_participants,
            start_time=start_time,
            end_time=end_time,
            is_private=is_private,
        )
        my_event.save()
        return my_event.id

    def throw_exception_if_invalid_category_location(self, category_id, location_id):
        try:
            CategoryLocation.objects.get(category_id=category_id, location_id=location_id)
        except CategoryLocation.DoesNotExist:
            raise ValidationError(self.invalid_category_location_message)

    def throw_exception_if_invalid_date(self, start_time, end_time):
        if end_time <= start_time:
            raise ValidationError(self.invalid_time_error_message)

    def throw_exception_if_invalid_poll_end_time(self, event_start_time, poll_end_time):
        time_zone = pytz.timezone('UTC')
        event_start_time = time_zone.localize(event_start_time)
        if poll_end_time >= event_start_time:
            raise ValidationError(self.invalid_poll_error)

    def join_event(self, user_id):
        # TODO- upadate user event table
        return 0

    def generate_teams(self, team_size):
        # Todo- send request to teams
        return 0

    def update_event_time(self, event_id, start_time, end_time):
        return 0


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
    objects = EvnetManager()

    def __str__(self) -> str:
        return self.name


class UserEvent(models.Model):
    userID = models.ForeignKey(Profile, on_delete=models.CASCADE)
    eventID = models.ForeignKey(Event, on_delete=models.CASCADE)
    teamID = models.ForeignKey(Teams, on_delete=models.CASCADE)
    isEventAdmin = models.BooleanField(default=False)
