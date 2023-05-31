import pytest
from ..models import Event


@pytest.mark.django_db
class TestEventList:
    def test_event_list(self, client, user1):
        events = Event.manager.all()
        client.force_login(user1.user)
        response = client.get(f'/{user1.user.id}/event/event_list/')
        assert response.status_code == 200
        for event in events:
            assert event.name in response.content.decode()

    def test_event_list_filter_category(self, client, user1, category1):
        events = Event.manager.all()
        client.force_login(user1.user)
        response = client.get(f'/{user1.user.id}/event/event_list/?Choose_Category={category1.name}')
        assert response.status_code == 200
        for event in events.filter(category=category1):
            assert event.name in response.content.decode()
        for event in events.exclude(category=category1):
            assert event.name not in response.content.decode()

    def test_event_list_filter_location(self, client, user1, location1):
        events = Event.manager.all()
        client.force_login(user1.user)
        response = client.get(f'/{user1.user.id}/event/event_list/?Choose_Location={location1.name}')
        assert response.status_code == 200
        for event in events.filter(location=location1):
            assert event.name in response.content.decode()
        for event in events.exclude(location=location1):
            assert event.name not in response.content.decode()

    def test_event_list_order_by_time(self, client, user1):
        events = Event.manager.all()
        client.force_login(user1.user)
        response = client.get(f'/{user1.user.id}/event/event_list/?Order_By=Time')
        assert response.status_code == 200
        events_ordered_by_time = sorted(events, key=lambda event: event.start_time)
        content = response.content.decode()
        event_names_in_html = [event.name for event in events_ordered_by_time if event.name in content]
        for i in range(len(events_ordered_by_time) - 1):
            assert event_names_in_html[i] == events_ordered_by_time[i].name

    def test_event_list_order_by_participants(self, client, user1):
        events = Event.manager.all()
        client.force_login(user1.user)
        response = client.get(f'/{user1.user.id}/event/event_list/?Order_By=Participants')
        assert response.status_code == 200
        events_ordered_by_participants = sorted(events, key=lambda event: event.max_participants)
        content = response.content.decode()
        event_names_in_html = [event.name for event in events_ordered_by_participants if event.name in content]
        for i in range(len(events_ordered_by_participants)):
            assert event_names_in_html[i] == events_ordered_by_participants[i].name
