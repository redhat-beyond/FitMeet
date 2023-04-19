from django.db import models
from category.models import Category
from location.models import Location
from category_location.models import CategoryLocation
from poll.models import Poll
from users.models import Profile
from teams.models import Teams
from django.core.exceptions import ValidationError
import pytz


class EventManager(models.Manager):
    invalid_category_location_message = (
        "The pair of category and location is not in category location table"
    )
    invalid_time_error_message = "Error - event end time cannot be equal or less than start time"
    invalid_poll_error = "Error- poll end time is late than the event start time"
    invalid_join_error = "Error - event reached max capacity"

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
        my_event_category = Category.objects.get(id=category_id)
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
            category=my_event_category,
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
        event_start_time = self.localize_datetime(event_start_time)
        if poll_end_time >= event_start_time:
            raise ValidationError(self.invalid_poll_error)

    def join_event(self, user_id, event_id):
        event = Event.objects.get(id=event_id)
        # TODO- upadate user event table
        if event.participants_num < event.max_participants:
            event.participants_num += 1
            event.save()
        else:
            raise ValidationError(self.invalid_join_error)
        return 0

    def generate_teams(self, team_size):
        # Todo- send request to teams
        return 0

    def update_event_time(self, event_id, start_time, end_time):
        event = Event.objects.get(id=event_id)
        if start_time < end_time:
            event.start_time = start_time
            event.end_time = end_time
            event.save()
        else:
            raise ValidationError(self.invalid_time_error_message)

    def update_category(self, event_id, category_id):
        event = Event.objects.get(id=event_id)
        self.throw_exception_if_invalid_category_location(
            category_id=category_id, location_id=event.location.id
        )
        updated_category = Category.objects.get(id=category_id)
        event.category = updated_category
        event.save()

    def update_location(self, event_id, location_id):
        event = Event.objects.get(id=event_id)
        self.throw_exception_if_invalid_category_location(
            category_id=event.category.id, location_id=location_id
        )
        updated_location = Location.objects.get(id=location_id)
        event.location = updated_location
        event.save()

    def localize_datetime(self, datetime):
        time_zone = pytz.timezone('UTC')
        return time_zone.localize(datetime)


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
    objects = EventManager()

    def __str__(self) -> str:
        return self.name


class UserEvent(models.Model):
    userID = models.ForeignKey(Profile, on_delete=models.CASCADE)
    eventID = models.ForeignKey(Event, on_delete=models.CASCADE)
    teamID = models.ForeignKey(Teams, on_delete=models.CASCADE)
    isEventAdmin = models.BooleanField(default=False)
