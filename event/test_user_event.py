from django.utils import timezone
from .models import UserEvent
from .models import Event
import pytest
from users.models import Profile
from teams.models import Teams
from django.contrib.auth import get_user_model


@pytest.fixture
def create_user():
    return get_user_model().objects.create_user(
        username='testuser',
        password='testpass'
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
def create_team():
    team = Teams.objects.create(
        name='team name'
    )
    return team


@pytest.fixture
def create_event():
    event = Event.objects.create(
        name='event name',
        max_participants=1,
        start_time=timezone.now(),
        end_time=timezone.now(),
    )
    return event


@pytest.fixture
def create_user_event(create_event, create_team, create_profile):
    user_event = UserEvent.objects.create(userID=create_profile,
                                          eventID=create_event,
                                          teamID=create_team,
                                          isEventAdmin=False)
    return user_event


@pytest.mark.django_db
class TestUserEventModel:

    def test_get_user_event(self, create_user_event):
        user_event = UserEvent.objects.get(pk=create_user_event.pk)
        assert user_event == create_user_event

    def test_delete_user_event(self, create_user_event):
        user_event = create_user_event
        user_event.delete()
        with pytest.raises(UserEvent.DoesNotExist):
            UserEvent.objects.get(pk=create_user_event.pk)
