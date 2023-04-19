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
def category_location(location_name=EVENT_NAME, category_name=CATEGORY):
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

        assert e.value.message == models.EvnetManager.invalid_category_location_message

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
        assert e.value.message == models.EvnetManager.invalid_time_error_message

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

    # def test_event_update(self):
    #     event = create_validate_event()
