from datetime import timedelta
from django.core.exceptions import ValidationError
import pytest
from django.utils import timezone
from .conftest import MAX_PART, DATETIME
from .. import models


@pytest.mark.django_db()
class TestEvent:
    def test_location_category_validation_correct(self, category_location1):
        try:
            models.Event.manager.verify_category_location(
                location_id=category_location1.location.id, category_id=category_location1.category.id
            )
            assert True
        except ValidationError as err:
            pytest.fail(f'An error occurred: {str(err)}')

    def test_location_category_validation_error(self, location1, category1):
        with pytest.raises(ValidationError) as err:
            models.Event.manager.verify_category_location(location_id=location1.id, category_id=category1.id)
        assert err.value.message == models.EventManager.invalid_category_location_message

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
            models.Event.manager.verfiy_event_date(start_date, end_date)
            assert True
        except ValidationError as err:
            pytest.fail(f'An error occurred: {str(err)}')

    @pytest.mark.parametrize(
        "start_date, end_date",
        [
            (timezone.now() + timedelta(days=1), timezone.now()),
            (timezone.now() + timedelta(milliseconds=3), timezone.now()),
            (DATETIME, DATETIME),
        ],
    )
    def test_time_validation_error(self, start_date, end_date):
        with pytest.raises(ValidationError) as err:
            models.Event.manager.verfiy_event_date(start_date, end_date)
        assert err.value.message == models.EventManager.invalid_time_error_message

    def test_poll_end_time_validator(self):
        with pytest.raises(ValidationError) as err:
            models.Event.manager.verify_poll_end_time(
                poll_end_time=timezone.now() + timedelta(days=1), event_start_time=timezone.now()
            )
        assert err.value.message == models.EventManager.invalid_poll_error

    def test_praticipants_validation(self):
        with pytest.raises(ValidationError) as err:
            models.Event.manager.verify_max_participants(max_participants=0, current_participants_num=1)
        assert err.value.message == models.EventManager.invalid_event_size_error

    def test_event_creation_via_manager_and_direct(self, event1, validate_event1):
        assert event1.name == validate_event1.name
        assert event1.location == validate_event1.location
        assert event1.category == validate_event1.category
        assert event1.max_participants == validate_event1.max_participants
        assert event1.max_participants == validate_event1.max_participants
        assert event1.participants_num == validate_event1.participants_num
        assert event1.start_time == validate_event1.start_time
        assert event1.end_time == validate_event1.end_time
        assert event1.is_private == validate_event1.is_private

    @pytest.mark.parametrize(
        "start_date, end_date",
        [
            (timezone.now(), timezone.now() + timedelta(days=1)),
            (timezone.now(), timezone.now() + timedelta(hours=3)),
            (timezone.now(), timezone.now() + timedelta(minutes=2)),
        ],
    )
    def test_event_update_time_correct(self, validate_event1, start_date, end_date):
        updated_event = models.Event.manager.update(
            event_id=validate_event1.id, start_time=start_date, end_time=end_date
        )
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
    def test_event_update_time_error(self, validate_event1, start_date, end_date):
        with pytest.raises(ValidationError) as err:
            models.Event.manager.update(event_id=validate_event1.id, start_time=start_date, end_time=end_date)
        assert err.value.message == models.EventManager.invalid_time_error_message

    def test_update_category_correct(self, validate_event1):
        cat = models.Category(name="Updated")
        cat.save()
        cat_loc = models.CategoryLocation(category=cat, location=validate_event1.location)
        cat_loc.save()
        updated_event = models.Event.manager.update(event_id=validate_event1.id, category_id=cat.id)
        assert updated_event.category.name == "Updated"

    def test_update_category_error(self, validate_event1):
        cat = models.Category(name="Updated")
        cat.save()
        with pytest.raises(ValidationError) as err:
            models.Event.manager.update(event_id=validate_event1.id, category_id=cat.id)
        assert err.value.message == models.EventManager.invalid_category_location_message

    def test_update_location_correct(self, validate_event1):
        location = models.Location(
            name="update", city="update", street="update", street_number=2, indoor=False, description="update"
        )
        location.save()
        cat_loc = models.CategoryLocation(location=location, category=validate_event1.category)
        cat_loc.save()
        updated_event = models.Event.manager.update(event_id=validate_event1.id, location_id=location.id)
        assert updated_event.location == location

    def test_update_location_error(self, validate_event1):
        with pytest.raises(ValidationError) as err:
            location = models.Location(
                name="update", city="update", street="update", street_number=2, indoor=False, description="update"
            )
            location.save()
            models.Event.manager.update(event_id=validate_event1.id, location_id=location.id)
        assert err.value.message == models.EventManager.invalid_category_location_message

    def test_update_max_participants_correct(self, validate_event1):
        updated_event = models.Event.manager.update(event_id=validate_event1.id, max_participants=MAX_PART + 10)
        assert updated_event.max_participants == MAX_PART + 10

    def test_update_max_participants_erro(self, validate_event1):
        with pytest.raises(ValidationError) as err:
            models.Event.manager.update(event_id=validate_event1.id, max_participants=0)
        assert err.value.message == models.EventManager.invalid_event_size_error

    def test_update_multipule_values(self, validate_event1):
        start_time = timezone.now() + timedelta(weeks=1)
        updated_event = models.Event.manager.update(
            event_id=validate_event1.id,
            name='updated',
            max_participants=MAX_PART + 3,
            start_time=start_time,
            end_time=start_time + timedelta(hours=3),
            is_private=True,
        )
        assert updated_event.name == 'updated'
        assert updated_event.max_participants == MAX_PART + 3
        assert updated_event.start_time == start_time
        assert updated_event.end_time == start_time + timedelta(hours=3)
        assert updated_event.is_private

    def test_update_nothing(self, validate_event1):
        update_event = models.Event.manager.update(event_id=validate_event1.id)
        assert update_event.name == validate_event1.name
        assert update_event.location == validate_event1.location
        assert update_event.category == validate_event1.category
        assert update_event.poll == validate_event1.poll
        assert update_event.start_time == validate_event1.start_time
        assert update_event.end_time == validate_event1.end_time
        assert update_event.is_private == validate_event1.is_private

    def test_join_participant_correct(self, validate_event1, user2):
        current_participants = validate_event1.participants_num
        assert models.Event.manager.join_event(user2.id, validate_event1.id)
        updated_event = models.Event.manager.get(id=validate_event1.id)
        assert updated_event.participants_num == current_participants + 1
        try:
            models.UserEvent.objects.get(userID=user2.id, eventID=validate_event1.id)
            assert True
        except models.UserEvent.DoesNotExist as err:
            pytest.fail(f'An error occurred: {str(err)}')

    def test_join_participant_error_reach_max(self, validate_event1, user2):
        validate_event1.participants_num = MAX_PART
        validate_event1.save()
        assert not models.Event.manager.join_event(user2.id, validate_event1.id)

    def test_join_participant_error_invalid_userid(self, validate_event1):
        participants_num = validate_event1.participants_num
        assert not models.Event.manager.join_event(122, validate_event1.id)
        assert participants_num == validate_event1.participants_num

    def test_object_deleted(self, validate_event1):
        validate_event1.delete()
        assert validate_event1 not in list(models.Event.manager.all())

    @pytest.mark.parametrize(
        "categories,result",
        [(['FootBall'], 5), (['FootBall', 'basketball'], 11), (['Baseball', 'gym', 'football'], 15), (['Chess'], 0)],
    )
    def test_filter_by_category(self, categories, result, event_data_set):
        query_set = models.Event.manager.search(categories=categories)
        assert len(query_set) == result

    @pytest.mark.parametrize(
        "location_name, result",
        [(["Tedi stadium"], 5), (["sportech", "Sami offer stadium"], 10), (["Stantiago Bernabeo stadium"], 0)],
    )
    def test_filter_by_location_name(self, location_name, result):
        query_set = models.Event.manager.search(location_names=location_name)
        assert len(query_set) == result

    @pytest.mark.parametrize(
        "cities,result",
        [
            (['Tel aviv'], 5),
            (['tel aviv', 'yaffo'], 10),
            (['jerusalem', 'Haifa', 'beer sheva'], 15),
            (['ness ziona'], 0),
        ],
    )
    def test_filter_by_location_city(self, cities, result):
        query_set = models.Event.manager.search(location_cities=cities)
        assert len(query_set) == result

    @pytest.mark.parametrize(
        "event_size,result",
        [
            ((8, True), 23),
            ((20, True), 15),
            ((50, False), 27),
            ((1, False), 0),
        ],
    )
    def test_filter_by_event_size(self, event_size, result):
        query_set = models.Event.manager.search(event_size=event_size)
        assert len(query_set) == result

    @pytest.mark.parametrize(
        "event_time,result",
        [
            ((timezone.now() + timedelta(days=2), True), 22),
            ((timezone.now() + timedelta(days=9), True), 10),
            ((timezone.now() + timedelta(weeks=2), False), 22),
            ((timezone.now() + timedelta(weeks=4), True), 0),
        ],
    )
    def test_filter_by_event_time(self, event_time, result):
        query_set = models.Event.manager.search(start_time=event_time)
        assert len(query_set) == result

    @pytest.mark.parametrize(
        "categories, location_city,result",
        [
            (['FootBall'], ['tel aviv'], 1),
            (['FootBall', 'Basketball'], ['tel aviv'], 2),
            (['FootBall'], ['tel aviv', 'beer sheva'], 2),
            (['chess'], ['bat yam'], 0),
        ],
    )
    def test_filter_by_category_location_city(self, categories, location_city, result):
        query_set = models.Event.manager.search(categories=categories, location_cities=location_city)
        assert len(query_set) == result

    @pytest.mark.parametrize(
        "event_time, event_size,result",
        [
            ((timezone.now() + timedelta(days=2), True), (8, True), 19),
            ((timezone.now() + timedelta(days=9), True), (20, True), 6),
            ((timezone.now() + timedelta(weeks=2), False), (50, False), 22),
        ],
    )
    def test_filter_by_event_time_and_size(self, event_time, event_size, result):
        query_set = models.Event.manager.search(event_size=event_size, start_time=event_time)
        assert len(query_set) == result

    def test_empty_filter(self):
        query_set = models.Event.manager.search()
        assert len(query_set) == 27

    def test_static_event(self):
        event = models.Event.manager.search(categories=["Soccer"], location_names=["Bloomfield"]).first()
        category = models.Category.objects.filter(name="Soccer").first()
        location = models.Location.objects.filter(name="Bloomfield").first()
        assert event.category == category
        assert event.location == location

    def test_leave_event(self, validate_event1, user1):
        models.Event.manager.leave_event(user_id=user1.id, event_id=validate_event1.id)
        users_in_event = models.UserEvent.objects.filter(eventID=validate_event1.id).values_list("userID", flat=True)
        assert user1 not in users_in_event

    @pytest.mark.parametrize(
        "participants_current_num, max_participants_num, result",
        [
            (2, 2, True),
            (1, 3, False),
            (4, 3, True),
        ],
    )
    def test_is_event_full(self, participants_current_num, max_participants_num, result, validate_event1):
        validate_event1.participants_num = participants_current_num
        validate_event1.max_participants = max_participants_num
        validate_event1.save()
        assert validate_event1.is_full() == result
