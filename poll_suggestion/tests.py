# from django.test import TestCase

# Create your tests here.
# from django.test import TestCase

# Create your tests here.
from poll.models import Poll, get_default_end_date
from .models import PollSuggestion
from django.test import TestCase
from datetime import datetime, timedelta
from django.utils import timezone
from poll.models import Poll
from event.models import Event
from category.models import Category
from location.models import Location
from category_location.models import CategoryLocation
from django.core.exceptions import ValidationError
import pytest

EVENT_NAME = "weight lifting"
CATEGORY = "Gym1"
LOCATION = "Holmes place Netanya"
MAX_PART = 10
IS_PRIVATE = False
DATETIME = datetime.now()
MAX_SUGEGSTIONS = 5
DATETIME = timezone.now()


@pytest.fixture
def setup_category_location():
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
def setup_event(setup_category_location):
    event = Event(
        category=setup_category_location.category,
        location=setup_category_location.location,
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
def setup_poll(setup_event):
    poll = Poll(event_id=setup_event, max_suggestions=MAX_SUGEGSTIONS, end_time=get_default_end_date())
    poll.save()
    return poll


@pytest.fixture
def set_up_poll_suggestion(setup_poll):
    poll_s = PollSuggestion.objects.create(time=datetime.now() + timedelta(days=3), poll_id=setup_poll)
    poll_s.save()
    return poll_s


@pytest.mark.django_db
class TestPollSuggestionModel:

    def test_create_poll_suggestion(self, set_up_poll_suggestion):
        poll_suggestion1 = PollSuggestion.objects.get(id=set_up_poll_suggestion.id)
        poll = poll_suggestion1.poll_id
        poll_s_from_db = poll.show_suggestions()
        return poll_s_from_db == poll_suggestion1
