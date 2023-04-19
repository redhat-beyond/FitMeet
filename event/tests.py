import pytest
from . import models
from django.core.exceptions import ValidationError
from datetime import timedelta, datetime

EVENT_NAME = "football with friends"
CATEGORY = "football"
LOCATION = "SAMI OFFER STUDIUM"
MAX_PART = 20
IS_PRIVATE = False
DATETIME = datetime.now() + timedelta(days=2)


@pytest.mark.django_db()
def create_sample_category_location(
    cat_name="test",
    loc_name="test",
    loc_city="test",
    loc_street="test",
    loc_street_num=1,
    loc_indoor=False,
    loc_des="test",
):
    loc = models.Location(
        name=loc_name,
        city=loc_city,
        street=loc_street,
        street_number=loc_street_num,
        indoor=loc_indoor,
        description=loc_des,
    )
    loc.save()
    cat = models.Category(name=cat_name)
    cat.save()
    return loc, cat


@pytest.fixture
def category_location(location_name=LOCATION, category_name=CATEGORY):
    location, category = create_sample_category_location(category_location, location_name)
    cat_loc = models.CategoryLocation(location=location, category=category)
    cat_loc.save()
    return cat_loc


@pytest.fixture
def poll():
    my_poll = models.Poll(max_suggestions=2, end_time=DATETIME + timedelta(days=-2))
    my_poll.save()
    return my_poll


@pytest.fixture
def event(category_location):
    my_poll = models.Poll(max_suggestions=2, end_time=DATETIME + timedelta(days=-2))
    my_poll.save()
    new_event = models.Event(
        category=category_location.category,
        location=category_location.location,
        poll=my_poll,
        name=EVENT_NAME,
        max_participants=MAX_PART,
        start_time=DATETIME,
        end_time=DATETIME + timedelta(hours=3),
        is_private=IS_PRIVATE,
    )
    new_event.save()
    return new_event


@pytest.fixture
def validate_event(category_location, poll):
    event_id = models.Event.objects.create_event(
        category_id=category_location.category.id,
        location_id=category_location.location.id,
        name=EVENT_NAME,
        max_participants=MAX_PART,
        start_time=DATETIME,
        end_time=DATETIME + timedelta(hours=3),
        is_private=IS_PRIVATE,
        poll_id=poll.id,
    )
    return models.Event.objects.get(id=event_id)


@pytest.fixture
def location():
    loc, cat = create_sample_category_location(
        cat_name="test",
        loc_name="New loc",
        loc_city="wonderland",
        loc_street="somewhere",
        loc_street_num=2,
        loc_indoor=False,
        loc_des="some words...",
    )
    loc.save()
    return loc


@pytest.mark.django_db()
class TestEvent:
    def test_loacation_category_validation_correct(self, category_location):
        result = models.Event.objects.throw_exception_if_invalid_category_location(
            location_id=category_location.location.id, category_id=category_location.category.id
        )
        assert result is None

    def test_loacation_category_validation_error(self):
        loc = models.Location(
            name="test2",
            city="test2",
            street="test2",
            street_number=2,
            indoor=False,
            description="test2",
        )
        loc.save()

        cat = models.Category(name="test2")
        cat.save()
        with pytest.raises(ValidationError) as e:
            models.Event.objects.throw_exception_if_invalid_category_location(
                location_id=loc.id, category_id=cat.id
            )

        assert e.value.message == models.EventManager.invalid_category_location_message

    @pytest.mark.parametrize(
        "start_date, end_date",
        [
            (datetime.now(), datetime.now() + timedelta(days=1)),
            (datetime.now(), datetime.now() + timedelta(hours=3)),
            (datetime.now(), datetime.now() + timedelta(minutes=2)),
        ],
    )
    def test_time_validation_correct(self, start_date, end_date):
        result = models.Event.objects.throw_exception_if_invalid_date(start_date, end_date)
        assert result is None

    @pytest.mark.parametrize(
        "start_date, end_date",
        [
            (datetime.now() + timedelta(days=1), datetime.now()),
            (datetime.now() + timedelta(milliseconds=3), datetime.now()),
            (DATETIME, DATETIME),
        ],
    )
    def test_time_validation_error(self, start_date, end_date):
        with pytest.raises(ValidationError) as e:
            models.Event.objects.throw_exception_if_invalid_date(start_date, end_date)
        assert e.value.message == models.EventManager.invalid_time_error_message

    def test_event_creation_via_manager_and_direct(self, event, validate_event):
        assert event.name == validate_event.name
        assert event.location == validate_event.location
        assert event.category == validate_event.category
        assert event.max_participants == validate_event.max_participants
        assert event.max_participants == validate_event.max_participants
        assert event.participants_num == validate_event.participants_num
        assert event.start_time.time() == validate_event.start_time.time()
        assert event.end_time.time() == validate_event.end_time.time()
        assert event.is_private == validate_event.is_private

    @pytest.mark.parametrize(
        "start_date, end_date",
        [
            (datetime.now(), datetime.now() + timedelta(days=1)),
            (datetime.now(), datetime.now() + timedelta(hours=3)),
            (datetime.now(), datetime.now() + timedelta(minutes=2)),
        ],
    )
    def test_event_update_time_correct(self, validate_event, start_date, end_date):
        models.Event.objects.update_event_time(validate_event.id, start_date, end_date)
        updated_event = models.Event.objects.get(id=validate_event.id)
        assert updated_event.start_time.time() == start_date.time()
        assert updated_event.end_time.time() == end_date.time()

    @pytest.mark.parametrize(
        "start_date, end_date",
        [
            (datetime.now() + timedelta(days=1), datetime.now()),
            (datetime.now() + timedelta(milliseconds=3), datetime.now()),
            (DATETIME, DATETIME),
        ],
    )
    def test_event_update_time_error(self, validate_event, start_date, end_date):
        with pytest.raises(ValidationError) as e:
            models.Event.objects.update_event_time(validate_event.id, start_date, end_date)
        assert e.value.message == models.EventManager.invalid_time_error_message

    def test_update_category_correct(self, validate_event):
        cat = models.Category(name="Updated")
        cat.save()
        cat_loc = models.CategoryLocation(category=cat, location=validate_event.location)
        cat_loc.save()
        models.Event.objects.update_category(validate_event.id, cat.id)
        updated_event = models.Event.objects.get(id=validate_event.id)
        assert updated_event.category.name == "Updated"

    def test_update_category_error(self, validate_event):
        cat = models.Category(name="Updated")
        cat.save()
        with pytest.raises(ValidationError) as e:
            models.Event.objects.update_category(validate_event.id, cat.id)
        assert e.value.message == models.EventManager.invalid_category_location_message

    def test_update_location_correct(self, validate_event, location):
        cat_loc = models.CategoryLocation(location=location, category=validate_event.category)
        cat_loc.save()
        models.Event.objects.update_location(validate_event.id, location.id)
        updated_event = models.Event.objects.get(id=validate_event.id)
        assert updated_event.location == location

    def test_update_location_error(self, validate_event, location):
        with pytest.raises(ValidationError) as e:
            models.Event.objects.update_location(validate_event.id, location.id)
        assert e.value.message == models.EventManager.invalid_category_location_message

    def test_join_participant_correct(self, validate_event):
        # Todo - remove hard coded user id
        current_participants = validate_event.participants_num
        models.Event.objects.join_event(3, validate_event.id)
        updated_event = models.Event.objects.get(id=validate_event.id)
        assert updated_event.participants_num == current_participants + 1

    def test_join_participant_error(self, validate_event):
        # Todo - remove hard coded user id
        validate_event.participants_num = MAX_PART
        validate_event.save()
        with pytest.raises(ValidationError) as e:
            models.Event.objects.join_event(3, validate_event.id)
        assert e.value.message == models.EventManager.invalid_join_error

    def test_object_deleted(self, validate_event):
        validate_event.delete()
        assert validate_event not in list(models.Event.objects.all())
