import pytest
from .models import Poll, get_default_end_date
from datetime import datetime, timedelta
from django.utils import timezone
from event.models import Event
from category.models import Category
from location.models import Location
from category_location.models import CategoryLocation

EVENT_NAME = "weight lifting"
CATEGORY = "Gym1"
LOCATION = "Holmes place Netanya"
MAX_PART = 10
IS_PRIVATE = False
DATETIME = datetime.now()


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
def poll1(category_location1):
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
    poll = Poll.objects.create(event_id=event, max_suggestions=5, end_time=get_default_end_date())
    poll.save()
    return poll


@pytest.mark.django_db
class TestPollModel:
    def test_max_suggestions_less_than_participants(self, poll1):
        poll_from_db = Poll.objects.get(id=poll1.id)
        assert poll_from_db.max_suggestions <= poll_from_db.event_id.max_participants

    def test_logical_poll_end_time(self, poll1):
        poll_from_db = Poll.objects.get(id=poll1.id)
        now = timezone.localtime(timezone.now())
        assert poll_from_db.end_time <= now + timedelta(days=365)

    def test_poll_end_time_before_event_end_time(self, poll1):
        poll_from_db = Poll.objects.get(id=poll1.id)
        assert poll_from_db.end_time < poll_from_db.event_id.end_time

    def test_poll_end_time_after_event_start_time(self, poll1):
        poll_from_db = Poll.objects.get(id=poll1.id)
        assert poll_from_db.end_time < poll_from_db.event_id.start_time

    def test_poll_retrieve_event(self, poll1):
        poll_from_db = Poll.objects.get(id=poll1.id)
        assert poll_from_db.event_id == poll1.event_id
