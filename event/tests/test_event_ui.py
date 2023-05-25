import re
import pytest
from django.utils import timezone
from pytest_django.asserts import assertRedirects
from ..forms import EventForm
from .. import models


@pytest.mark.django_db()
class TestEventUi:
    def test_create_event_get_method(self, client, create_url):
        response = client.get(create_url)
        assert response.status_code == 200
        assert isinstance(response.context['form'], EventForm)

    def test_create_event_post_method_correct_submition(self, client, create_url, create_event_form_data1):
        response = client.post(create_url, data=create_event_form_data1)
        event_id = models.Event.manager.last().id
        user_id = re.search(r'/(\d+)/event/create/', create_url).group(1)
        expected_url = f'/{user_id}/event/info/?id={event_id}'
        assert response.status_code == 302
        assert response.url == expected_url
        assertRedirects(response, expected_url, status_code=302, target_status_code=200)

    def test_create_invalid_form_field(self, client, create_url, create_event_form_data1):
        location = models.Location.objects.last()
        create_event_form_data1['location'] = location
        response = client.post(create_url, data=create_event_form_data1)
        assert response.status_code == 409
        assert "Select a valid choice. That choice is not one of the available choices." == response.context['error']

    def test_create_logical_violation(self, client, create_url, create_event_form_data1):
        create_event_form_data1['end_time'] = timezone.now()
        response = client.post(create_url, data=create_event_form_data1)
        assert response.status_code == 409
        assert models.EventManager.invalid_time_error_message == response.context['error']

    def test_event_info(self, client, first_event_info_url):
        response = client.get(first_event_info_url)
        assert response.status_code == 200
