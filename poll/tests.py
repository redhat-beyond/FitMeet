import pytest
from .models import Poll, get_default_end_date
from datetime import datetime, timedelta
from django.utils import timezone
from event.models import Event
from category.models import Category
from location.models import Location
from category_location.models import CategoryLocation
from poll_suggestion.models import PollSuggestion
from django.core.exceptions import ValidationError

EVENT_NAME = "weight lifting"
CATEGORY = "Gym1"
LOCATION = "Holmes place Netanya"
MAX_PART = 10
IS_PRIVATE = False
MAX_SUGEGSTIONS = 5
DATETIME = timezone.now()


@pytest.fixture
def category_location1():
    loc = Location(
        name=LOCATION,
        city="test city",
        street="test street",
        street_number=1,
        indoor=False,
        description="test description",
    )
    loc.save()
    cat = Category(name=CATEGORY)
    cat.save()
    cat_loc = CategoryLocation(location=loc, category=cat)
    cat_loc.save()
    return cat_loc


@pytest.fixture
def event1(category_location1):
    event = Event(
        category=category_location1.category,
        location=category_location1.location,
        poll=None,
        name=EVENT_NAME,
        max_participants=MAX_PART,
        start_time=DATETIME + timedelta(days=2),
        end_time=DATETIME + timedelta(days=3),
        is_private=IS_PRIVATE,
    )
    event.save()
    return event


@pytest.fixture
def poll1(event1):
    poll = Poll.objects.create(event_id=event1, max_suggestions=MAX_SUGEGSTIONS, end_time=get_default_end_date())
    poll.save()
    return poll


@pytest.mark.django_db
class TestPollModel:
    def test_max_suggestions_less_than_participants(self, poll1):
        poll_from_db = Poll.objects.get(id=poll1.id)
        assert poll_from_db.max_suggestions <= poll_from_db.event_id.max_participants

    def test_logical_poll_end_time(self, poll1):
        poll_from_db = Poll.objects.get(id=poll1.id)
        assert poll_from_db.end_time <= DATETIME + timedelta(days=365)

    def test_poll_end_time_before_event_end_time(self, poll1):
        poll_from_db = Poll.objects.get(id=poll1.id)
        assert poll_from_db.end_time < poll_from_db.event_id.end_time

    def test_poll_end_time_after_event_start_time(self, poll1):
        poll_from_db = Poll.objects.get(id=poll1.id)
        assert poll_from_db.end_time < poll_from_db.event_id.start_time

    def test_poll_retrieve_event(self, poll1):
        poll_from_db = Poll.objects.get(id=poll1.id)
        assert poll_from_db.event_id == poll1.event_id

    def test_verify_poll_end_time_raises_validation_error(self, poll1):
        with pytest.raises(ValidationError) as err:
            poll1.verify_poll_end_time(
                event_start_time=poll1.event_id.start_time,
                poll_end_time=poll1.event_id.start_time + timedelta(hours=1)
            )
        assert err.value.message == Poll.invalid_poll_error

    def test_create_poll_with_invalid_end_time(self, event1):
        with pytest.raises(ValidationError) as err:
            Poll.create_poll(event=event1,
                             max_suggestions=5,
                             end_time=event1.start_time + timedelta(hours=1),
                             )
        assert err.value.message == Poll.invalid_poll_error

    def test_create_valid_poll(self, event1):
        poll = Poll.create_poll(event=event1,
                                max_suggestions=MAX_SUGEGSTIONS,
                                end_time=DATETIME,
                                )
        assert poll.event_id == event1
        assert poll.max_suggestions == MAX_SUGEGSTIONS
        assert poll.end_time == DATETIME

    def test_is_active_false(self, poll1):
        poll_from_db = Poll.objects.get(id=poll1.id)
        poll_from_db.end_time = timezone.now() - timedelta(hours=1)
        poll_from_db.save()
        assert not poll_from_db.is_active()

    def test_show_suggestions(self, poll1):
        times = [(datetime.now() + timedelta(minutes=10 * i)) for i in range(1, 4)]
        for time in times:
            poll_suggestion = PollSuggestion(poll_id=poll1, time=time)
            poll_suggestion.save()

        suggestions = poll1.show_suggestions()
        assert suggestions.count() == 3

        suggestion_times = [suggestion.time for suggestion in suggestions]
        datetime_objects = [dt.replace(tzinfo=None) for dt in suggestion_times]

        for time in times:
            assert time in datetime_objects

    def test_time_remaining_positive(self, poll1):
        poll_from_db = Poll.objects.get(id=poll1.id)
        time_remaining = poll_from_db.time_remaining()
        assert time_remaining > timedelta()
        assert pytest.approx(time_remaining.total_seconds()) == (poll_from_db.end_time - timezone.now()).total_seconds()
