from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import pytest
from . import models


EVENT_NAME = "football with friends"
MAX_PART = 20
IS_PRIVATE = False
DATETIME = timezone.now() + timedelta(days=2)
POLL_END_TIME = timezone.now()
POLL_MAX_SUGGESTIONS = 3


@pytest.fixture
def category1():
    category = models.Category(name="test1")
    category.save()
    return category


@pytest.fixture
def location1():
    location = models.Location(
        name="test1", city="test1", street="test1", street_number=1, indoor=False, description="test1"
    )
    location.save()
    return location


@pytest.fixture
def category_location1(category1, location1):
    cat_loc = models.CategoryLocation(category=category1, location=location1)
    cat_loc.save()
    return cat_loc


@pytest.fixture
def user1():
    user = User.objects.create_user(username='test', password='test', email='myemail@example.com')
    profile = models.Profile(
        user=user, date_of_birth=timezone.now(), phone_number="test", image_url="http://127.0.0.1:8000/"
    )
    profile.save()
    return profile


@pytest.fixture
def user2():
    user = User.objects.create_user(username='test1', password='test1', email='myemail1@example.com')
    profile = models.Profile(
        user=user, date_of_birth=timezone.now(), phone_number="test1", image_url="http://127.0.0.1:8001/"
    )
    profile.save()
    return profile


@pytest.fixture
def poll1():
    poll = models.Poll(max_suggestions=POLL_MAX_SUGGESTIONS, end_time=POLL_END_TIME)
    poll.save()
    return poll


@pytest.fixture
def event_id_1(category_location1, poll1):
    new_event = models.Event(
        category=category_location1.category,
        location=category_location1.location,
        poll=poll1,
        name=EVENT_NAME,
        max_participants=MAX_PART,
        start_time=DATETIME,
        end_time=DATETIME + timedelta(hours=3),
        is_private=IS_PRIVATE,
    )
    new_event.save()
    return new_event.id


@pytest.fixture
def validate_event_id_1(category_location1, user1):
    event_id = models.Event.objects.create_event(
        category_id=category_location1.category.id,
        location_id=category_location1.location.id,
        name=EVENT_NAME,
        max_participants=MAX_PART,
        start_time=DATETIME,
        end_time=DATETIME + timedelta(hours=3),
        is_private=IS_PRIVATE,
        poll_end_time=POLL_END_TIME,
        poll_suggestions=POLL_MAX_SUGGESTIONS,
        user_id=user1.id,
    )
    return event_id


@pytest.mark.django_db()
class TestEvent:
    def test_location_category_validation_correct(self, category_location1):
        try:
            models.Event.objects.verify_category_location(
                location_id=category_location1.location.id, category_id=category_location1.category.id
            )
            assert True
        except ValidationError as e:
            pytest.fail(f'An error occurred: {str(e)}')

    def test_location_category_validation_error(self, location1, category1):
        with pytest.raises(ValidationError) as e:
            models.Event.objects.verify_category_location(location_id=location1.id, category_id=category1.id)
        assert e.value.message == models.EventManager.invalid_category_location_message

    @pytest.mark.parametrize(
        "start_date, end_date",
        [
            (timezone.now() + timedelta(days=1), timezone.now() + timedelta(days=2)),
            (timezone.now() + timedelta(hours=7), timezone.now() + timedelta(hours=10)),
            (timezone.now() + timedelta(minutes=1), timezone.now() + timedelta(minutes=2)),
        ],
    )
    def test_time_validation_correct(self, start_date, end_date):
        try:
            models.Event.objects.verfiy_event_date(start_date, end_date)
            assert True
        except ValidationError as e:
            pytest.fail(f'An error occurred: {str(e)}')

    @pytest.mark.parametrize(
        "start_date, end_date",
        [
            (timezone.now() + timedelta(days=1), timezone.now()),
            (timezone.now() + timedelta(milliseconds=3), timezone.now()),
            (DATETIME, DATETIME),
        ],
    )
    def test_time_validation_error(self, start_date, end_date):
        with pytest.raises(ValidationError) as e:
            models.Event.objects.verfiy_event_date(start_date, end_date)
        assert e.value.message == models.EventManager.invalid_time_error_message

    def test_poll_end_time_validator(self):
        with pytest.raises(ValidationError) as e:
            models.Event.objects.verify_poll_end_time(
                poll_end_time=timezone.now() + timedelta(days=1), event_start_time=timezone.now()
            )
        assert e.value.message == models.EventManager.invalid_poll_error

    def test_event_creation_via_manager_and_direct(self, event_id_1, validate_event_id_1):
        event1 = models.Event.objects.get(id=event_id_1)
        validate_event = models.Event.objects.get(id=validate_event_id_1)
        assert event1.name == validate_event.name
        assert event1.location == validate_event.location
        assert event1.category == validate_event.category
        assert event1.max_participants == validate_event.max_participants
        assert event1.max_participants == validate_event.max_participants
        assert event1.participants_num == validate_event.participants_num
        assert event1.start_time == validate_event.start_time
        assert event1.end_time == validate_event.end_time
        assert event1.is_private == validate_event.is_private

    @pytest.mark.parametrize(
        "start_date, end_date",
        [
            (timezone.now(), timezone.now() + timedelta(days=1)),
            (timezone.now(), timezone.now() + timedelta(hours=3)),
            (timezone.now(), timezone.now() + timedelta(minutes=2)),
        ],
    )
    def test_event_update_time_correct(self, validate_event_id_1, start_date, end_date):
        models.Event.objects.update_event_time(validate_event_id_1, start_date, end_date)
        updated_event = models.Event.objects.get(id=validate_event_id_1)
        assert updated_event.start_time.time() == start_date.time()
        assert updated_event.end_time.time() == end_date.time()

    @pytest.mark.parametrize(
        "start_date, end_date",
        [
            (timezone.now() + timedelta(days=1), timezone.now()),
            (timezone.now() + timedelta(milliseconds=3), timezone.now()),
            (DATETIME, DATETIME),
        ],
    )
    def test_event_update_time_error(self, validate_event_id_1, start_date, end_date):
        with pytest.raises(ValidationError) as e:
            models.Event.objects.update_event_time(validate_event_id_1, start_date, end_date)
        assert e.value.message == models.EventManager.invalid_time_error_message

    def test_update_category_correct(self, validate_event_id_1):
        validate_event = models.Event.objects.get(id=validate_event_id_1)
        cat = models.Category(name="Updated")
        cat.save()
        cat_loc = models.CategoryLocation(category=cat, location=validate_event.location)
        cat_loc.save()
        models.Event.objects.update_category(validate_event.id, cat.id)
        updated_event = models.Event.objects.get(id=validate_event.id)
        assert updated_event.category.name == "Updated"

    def test_update_category_error(self, validate_event_id_1):
        validate_event = models.Event.objects.get(id=validate_event_id_1)
        cat = models.Category(name="Updated")
        cat.save()
        with pytest.raises(ValidationError) as e:
            models.Event.objects.update_category(validate_event.id, cat.id)
        assert e.value.message == models.EventManager.invalid_category_location_message

    def test_update_location_correct(self, validate_event_id_1):
        validate_event = models.Event.objects.get(id=validate_event_id_1)
        location = models.Location(
            name="update", city="update", street="update", street_number=2, indoor=False, description="update"
        )
        location.save()
        cat_loc = models.CategoryLocation(location=location, category=validate_event.category)
        cat_loc.save()
        models.Event.objects.update_location(validate_event.id, location.id)
        updated_event = models.Event.objects.get(id=validate_event.id)
        assert updated_event.location == location

    def test_update_location_error(self, validate_event_id_1):
        validate_event = models.Event.objects.get(id=validate_event_id_1)
        with pytest.raises(ValidationError) as e:
            location = models.Location(
                name="update", city="update", street="update", street_number=2, indoor=False, description="update"
            )
            location.save()
            models.Event.objects.update_location(validate_event.id, location.id)
        assert e.value.message == models.EventManager.invalid_category_location_message

    def test_join_participant_correct(self, validate_event_id_1, user2):
        validate_event = models.Event.objects.get(id=validate_event_id_1)
        current_participants = validate_event.participants_num
        assert models.Event.objects.join_event(user2.id, validate_event.id)
        updated_event = models.Event.objects.get(id=validate_event.id)
        assert updated_event.participants_num == current_participants + 1
        try:
            models.UserEvent.objects.get(userID=user2.id, eventID=validate_event_id_1)
            assert True
        except models.UserEvent.DoesNotExist as e:
            pytest.fail(f'An error occurred: {str(e)}')

    def test_join_participant_error_reach_max(self, validate_event_id_1, user2):
        validate_event = models.Event.objects.get(id=validate_event_id_1)
        validate_event.participants_num = MAX_PART
        validate_event.save()
        assert not models.Event.objects.join_event(user2.id, validate_event.id)

    def test_join_participant_error_invalid_userid(self, validate_event_id_1):
        validate_event = models.Event.objects.get(id=validate_event_id_1)
        participants_num = validate_event.participants_num
        assert not models.Event.objects.join_event(122, validate_event_id_1)
        assert participants_num == validate_event.participants_num

    def test_object_deleted(self, validate_event_id_1):
        validate_event = models.Event.objects.get(id=validate_event_id_1)
        validate_event.delete()
        assert validate_event not in list(models.Event.objects.all())
