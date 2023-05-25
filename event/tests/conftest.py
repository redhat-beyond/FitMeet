from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
import pytest
from typing import List
from .. import models


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
        user=user, date_of_birth=timezone.now(), phone_number="test", image='default.jpg'
    )
    profile.save()
    return profile


@pytest.fixture
def user2():
    user = User.objects.create_user(username='test1', password='test1', email='myemail1@example.com')
    profile = models.Profile(
        user=user, date_of_birth=timezone.now(), phone_number="test1", image='default.jpg'
    )
    profile.save()
    return profile


@pytest.fixture
def poll1():
    poll = models.Poll(max_suggestions=POLL_MAX_SUGGESTIONS, end_time=POLL_END_TIME)
    poll.save()
    return poll


@pytest.fixture
def event1(category_location1, poll1):
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
    return new_event


@pytest.fixture
def validate_event1(category_location1, user1):
    event_id = models.Event.manager.create_event(
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
    event = models.Event.manager.get(id=event_id)
    return event


@pytest.fixture(scope="session")
def categories1(django_db_blocker) -> List[models.Category]:
    with django_db_blocker.unblock():
        query_set = models.Category.objects.all()
        query_set = list(query_set)[:5]
    return query_set


@pytest.fixture(scope="session")
def locations1(django_db_blocker) -> List[models.Location]:
    with django_db_blocker.unblock():
        names = ['Sportech', 'Sami offer stadium', 'Terner stadium', 'Tedi Stadium', 'Bluemfield Stadium']
        cities = ['Tel Aviv', 'Haifa', 'Beer Sheva', 'Jerusalem', 'Yaffo']
        locations_lst = []
        for location_name, city in zip(names, cities):
            new_location = models.Location(
                name=location_name, city=city, street='test', street_number=1, indoor=False, description='test'
            )
            new_location.save()
            locations_lst.append(new_location)
    return locations_lst


@pytest.fixture(scope="session")
def categories_locations1(django_db_blocker, categories1, locations1) -> List[models.CategoryLocation]:
    with django_db_blocker.unblock():
        categories_locations = []
        for category in categories1:
            for location in locations1:
                cat_loc = models.CategoryLocation(category=category, location=location)
                cat_loc.save()
                categories_locations.append(cat_loc)
    return categories_locations


@pytest.fixture(scope="session")
def users1(django_db_blocker) -> List[models.Profile]:
    with django_db_blocker.unblock():
        users = []
        for i in range(25):
            user = User.objects.create_user(username=f'user{i}', password=f'password{i}', email=f'user{i}@example.com')
            profile = models.Profile(
                user=user, date_of_birth=timezone.now(), phone_number=f"user{i}", image='default.jpg'
            )
            profile.save()
            users.append(profile)

    return users


@pytest.fixture(scope="session")
def time_samples(django_db_blocker):
    with django_db_blocker.unblock():
        current_time = timezone.now()
        lst = [
            current_time + timedelta(days=1),
            current_time + timedelta(days=3),
            current_time + timedelta(weeks=1),
            current_time + timedelta(days=3, weeks=1),
            current_time + timedelta(weeks=3),
        ]
    return lst


@pytest.fixture(scope="session")
def event_data_set(django_db_blocker, categories_locations1, users1, time_samples):
    with django_db_blocker.unblock():
        for index, user in enumerate(users1):
            cat_loc = categories_locations1.pop()
            start_time = time_samples[index % len(time_samples)]
            end_time = start_time + timedelta(hours=3)
            poll_end_time = start_time + timedelta(days=-1)
            models.Event.manager.create_event(
                category_id=cat_loc.category.id,
                location_id=cat_loc.location.id,
                max_participants=2 * index + 2,
                name=f'test event {index}',
                start_time=start_time,
                end_time=end_time,
                is_private=index > 15,
                poll_end_time=poll_end_time,
                poll_suggestions=3,
                user_id=user.id,
            )


@pytest.fixture
def base_url(db, user1):
    return f'/{user1.id}/event/'


@pytest.fixture
def create_url(base_url):
    return base_url + 'create/'


@pytest.fixture
def first_event_info_url(base_url):
    event = models.Event.manager.first()
    return f'{base_url}info/?id={event.id}'


@pytest.fixture
def create_event_form_data1(category_location1):
    return {
        'name': EVENT_NAME,
        'category': category_location1.category.id,
        'location': category_location1.location.id,
        'max_participants': MAX_PART,
        'start_time': DATETIME + timedelta(days=2),
        'end_time': DATETIME + timedelta(days=2, hours=3),
        'poll_end_time': DATETIME + timedelta(days=1),
        'poll_max_suggestions': POLL_MAX_SUGGESTIONS,
        'is_private': IS_PRIVATE,
    }
