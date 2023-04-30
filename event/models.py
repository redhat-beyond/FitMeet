from django.db import models, transaction, IntegrityError, DatabaseError
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone
from category.models import Category
from location.models import Location
from category_location.models import CategoryLocation
from poll.models import Poll
from users.models import Profile
from teams.models import Teams


class EventManager(models.Manager):
    invalid_category_location_message = "The pair of category and location is not in category location table"
    invalid_time_error_message = "Error - event end time cannot be equal or less than start time"
    invalid_poll_error = "Error- poll end time is late than the event start time"
    invalid_event_size_error = "Error - the number of max participants exeeds the maximum"

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
        poll_end_time,
        poll_suggestions,
        user_id,
    ):
        with transaction.atomic():
            # Check if category and location are valid
            self.verify_category_location(category_id=category_id, location_id=location_id)
            my_event_category = Category.objects.get(id=category_id)
            my_event_location = Location.objects.get(id=location_id)

            # Check start_time and time
            self.verfiy_event_date(start_time=start_time, end_time=end_time)

            # Check participants number
            self.verify_max_participants(max_participants=max_participants, current_participants_num=1)

            # validate poll time and create poll
            self.verify_poll_end_time(poll_end_time=poll_end_time, event_start_time=start_time)
            my_poll = Poll(max_suggestions=poll_suggestions, end_time=end_time)
            my_poll.save()

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

            # Update user event table
            user = Profile.objects.get(id=user_id)
            user_event = UserEvent(userID=user, eventID=my_event, isEventAdmin=True)
            user_event.save()

            # Set event id to poll
            my_poll.event_id = my_event
            my_poll.save()

            return my_event.id

    def verify_category_location(self, category_id, location_id):
        try:
            CategoryLocation.objects.get(category_id=category_id, location_id=location_id)
        except CategoryLocation.DoesNotExist:
            raise ValidationError(self.invalid_category_location_message)

    def verfiy_event_date(self, start_time, end_time):
        if end_time <= start_time or start_time <= timezone.now():
            raise ValidationError(self.invalid_time_error_message)

    def verify_poll_end_time(self, event_start_time, poll_end_time):
        if poll_end_time >= event_start_time:
            raise ValidationError(self.invalid_poll_error)

    def verify_max_participants(self, max_participants, current_participants_num):
        if max_participants <= current_participants_num:
            raise ValidationError(self.invalid_event_size_error)

    def join_event(self, user_id, event_id):
        try:
            with transaction.atomic():
                event = Event.manager.get(id=event_id)
                user = Profile.objects.get(id=user_id)
                self.verify_max_participants(
                    max_participants=event.max_participants, current_participants_num=event.participants_num
                )
                event.participants_num += 1
                event.save()
                user_event = UserEvent(
                    eventID=event,
                    userID=user,
                )
                user_event.save()
        except (ValidationError, DatabaseError, IntegrityError, ObjectDoesNotExist):
            return False

        return True

    def update(
        self,
        event_id,
        category_id=None,
        location_id=None,
        name=None,
        max_participants=None,
        start_time=None,
        end_time=None,
        is_private=None,
    ):
        event = Event.manager.get(id=event_id)
        if category_id:
            self.update_category(event, category_id)
        if location_id:
            self.update_location(event, location_id)
        if name:
            event.name = name
        if max_participants is not None:
            self.update_max_participants(event, max_participants)
        if start_time or end_time:
            self.update_event_time(event, start_time, end_time)
        if is_private is not None:
            event.is_private = is_private

        event.save()
        return event

    def update_max_participants(self, event, max_participants):
        self.verify_max_participants(max_participants=max_participants, current_participants_num=event.participants_num)
        event.max_participants = max_participants

    def update_event_time(self, event, start_time, end_time):
        if end_time <= start_time:
            raise ValidationError(self.invalid_time_error_message)
        event.start_time = start_time
        event.end_time = end_time

    def update_category(self, event, category_id):
        self.verify_category_location(category_id=category_id, location_id=event.location.id)
        event.category = Category.objects.get(id=category_id)

    def update_location(self, event, location_id):
        self.verify_category_location(category_id=event.category.id, location_id=location_id)
        event.location = Location.objects.get(id=location_id)


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
    manager = EventManager()

    def __str__(self) -> str:
        return self.name


class UserEvent(models.Model):
    userID = models.ForeignKey(Profile, on_delete=models.CASCADE)
    eventID = models.ForeignKey(Event, on_delete=models.CASCADE)
    teamID = models.ForeignKey(Teams, null=True, default=None, on_delete=models.CASCADE)
    isEventAdmin = models.BooleanField(default=False)
