import pytest

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone
from django.contrib.auth import get_user_model

from event.models import UserEvent, Event
from location.models import Location
from category.models import Category
from users.models import Profile
from .models import Teams

TEAM1 = 'Team 1'
LONG_NAME = 'A' * 32
EMPTY_NAME = ''


@pytest.fixture
def create_user():
    return get_user_model().objects.create_user(
        username='test_user',
        password='test_pass'
    )


@pytest.fixture
def create_profile(create_user):
    profile = Profile.objects.create(
        user=create_user,
        date_of_birth=timezone.now(),
        phone_number='052',
    )
    return profile


@pytest.fixture
def user_list():
    user_list = []
    for i in range(5):
        user_list.append(get_user_model().objects.create_user(
            username=f'test_user{i}',
            password='test_pass'
        ))
    return user_list


@pytest.fixture
def profile_list(user_list):
    profile_list = []
    for i in range(5):
        profile_list.append(Profile.objects.create(
            user=user_list[i],
            date_of_birth=timezone.now(),
            phone_number='052',
        ))
    return profile_list


@pytest.fixture
def create_team():
    team = Teams.objects.create(
        name='team name'
    )
    return team


@pytest.fixture
def location1():
    loc = Location(
        name="LOCATION",
        city="test city",
        street="test street",
        street_number=1,
        indoor=False,
        description="test description",
    )
    loc.save()
    return loc


@pytest.fixture
def category1():
    cat = Category(name="CATEGORY")
    cat.save()
    return cat


@pytest.fixture
def create_event(category1, location1):
    event = Event(
        category=category1,
        location=location1,
        poll=None,
        name="event",
        max_participants=10,
        start_time=timezone.now(),
        end_time=timezone.now(),
        is_private=True, )
    event.save()
    return event


@pytest.fixture
def create_user_event(create_event, create_team, create_profile):
    user_event = UserEvent.objects.create(userID=create_profile,
                                          eventID=create_event,
                                          teamID=create_team,
                                          isEventAdmin=False)
    return user_event


@pytest.fixture
def user_event_list(create_event, profile_list):
    user_event_list = []
    for i in range(5):
        user_event_list.append(UserEvent.objects.create(userID=profile_list[i],
                                                        eventID=create_event,
                                                        isEventAdmin=False))

    return user_event_list


@pytest.mark.django_db
class TestTeamsModel:
    @pytest.mark.parametrize(
        "invalid_name",
        [EMPTY_NAME, LONG_NAME],
    )
    def test_create_team_with_invalid_name(self, invalid_name):
        with pytest.raises(ValidationError):
            Teams.objects.create(name=LONG_NAME).full_clean()

    def test_create_team_with_taken_name(self):
        Teams.objects.create(name=TEAM1)
        with pytest.raises(IntegrityError):
            Teams.objects.create(name=TEAM1)

    def test_save(self):
        team1 = Teams(name=TEAM1)
        team1.save()
        assert team1 in Teams.objects.all()

    def test_generate_teams(self, user_event_list, create_event):
        for user_event in user_event_list:
            assert user_event.teamID is None

        Teams.generate_teams(create_event)
        generated_user_event_list = UserEvent.objects.filter(eventID=create_event)
        assert len(generated_user_event_list) == len(user_event_list)
        count_team1 = 0
        count_team2 = 0
        for user_event in generated_user_event_list:
            if user_event.teamID.name == "Team1":
                count_team1 += 1
            elif user_event.teamID.name == "Team2":
                count_team2 += 1
        team_size = len(generated_user_event_list) // 2
        assert team_size == count_team1
        assert len(generated_user_event_list) - team_size == count_team2
