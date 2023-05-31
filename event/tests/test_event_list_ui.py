import pytest
from ..models import Event


@pytest.fixture
def all_events():
    return Event.manager.all()


@pytest.fixture
def logged_in_client(client, user1):
    client.force_login(user1.user)
    return client


@pytest.mark.django_db
class TestEventList:
    def test_event_list(self, logged_in_client, user1, all_events):
        response = logged_in_client.get(f'/{user1.user.id}/event/event_list/')
        assert response.status_code == 200
        resp_content = response.content.decode()
        for event in all_events:
            assert event.name in resp_content

    def test_event_list_filter_category(self, logged_in_client, user1, all_events, category1):
        response = logged_in_client.get(f'/{user1.user.id}/event/event_list/?Choose_Category={category1.name}')
        assert response.status_code == 200
        resp_content = response.content.decode()
        for event in all_events.filter(category=category1):
            assert event.name in resp_content
        for event in all_events.exclude(category=category1):
            assert event.name not in resp_content

    def test_event_list_filter_location(self, logged_in_client, user1, all_events, location1):
        response = logged_in_client.get(f'/{user1.user.id}/event/event_list/?Choose_Location={location1.name}')
        assert response.status_code == 200
        resp_content = response.content.decode()
        for event in all_events.filter(location=location1):
            assert event.name in resp_content
        for event in all_events.exclude(location=location1):
            assert event.name not in resp_content

    def test_event_list_order_by_time(self, logged_in_client, user1, all_events):
        response = logged_in_client.get(f'/{user1.user.id}/event/event_list/?Order_By=Time')
        assert response.status_code == 200
        events_ordered_by_time = sorted(all_events, key=lambda event: event.start_time)
        resp_content = response.content.decode()
        event_names_in_html = [event.name for event in events_ordered_by_time if event.name in resp_content]
        for i in range(len(events_ordered_by_time) - 1):
            assert event_names_in_html[i] == events_ordered_by_time[i].name

    def test_event_list_order_by_participants(self, logged_in_client, user1, all_events):
        response = logged_in_client.get(f'/{user1.user.id}/event/event_list/?Order_By=Participants')
        assert response.status_code == 200
        events_ordered_by_participants = sorted(all_events, key=lambda event: event.max_participants)
        resp_content = response.content.decode()
        event_names_in_html = [event.name for event in events_ordered_by_participants if event.name in resp_content]
        for i in range(len(events_ordered_by_participants)):
            assert event_names_in_html[i] == events_ordered_by_participants[i].name
