import string
import re
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import pytest
from .models import Location

LOCATION_NAME = "location1"
CITY = "city1"
STREET = "street1"
STREET_NUMBER = 1
INDOOR = False
DESCRIPTION = "description1"

LOCATION_NAME_NEW = "location2"
CITY_NEW = 'city2'
STREET_NEW = 'street2'
STREET_NUMBER_NEW = 2
INDOOR_NEW = True
DESCRIPTION_NEW = 'description2'

LONG_FIELD = "a" * 45
EMPTY_FIELD = ''
SPECIAL_CHARACTERS = re.sub("[&_.,-]", "", string.punctuation)


@pytest.fixture
def location1():
    location1 = Location.objects.create(name=LOCATION_NAME, city=CITY, street=STREET,
                                        street_number=STREET_NUMBER, indoor=INDOOR, description=DESCRIPTION)
    location1.save()
    return location1


@pytest.mark.django_db
class TestLocationModel:

    def test_location_with_same_name(self, location1):
        assert location1.name == LOCATION_NAME
        with pytest.raises(IntegrityError):
            Location.objects.create(name=LOCATION_NAME, city=CITY_NEW, street=STREET_NEW,
                                    street_number=STREET_NUMBER_NEW, indoor=INDOOR_NEW,
                                    description=DESCRIPTION_NEW)

    @pytest.mark.parametrize("name, city, street, street_number, indoor, description", [
        (EMPTY_FIELD, CITY, STREET, STREET_NUMBER, INDOOR, DESCRIPTION),  # empty name
        (LOCATION_NAME, LONG_FIELD, STREET, STREET_NUMBER, INDOOR, DESCRIPTION),  # long city name
        (LOCATION_NAME, CITY, SPECIAL_CHARACTERS, STREET_NUMBER, INDOOR, DESCRIPTION),  # street name with special chars
    ],
                             )
    def test_create_location_with_invalid_values(self, name, city, street, street_number, indoor, description):
        with pytest.raises(ValidationError):
            Location.objects.create(name=name, city=city, street=street, street_number=street_number,
                                    indoor=indoor, description=description).full_clean()

    @pytest.mark.parametrize(
        "valid_name",
        ['b', 'B', 'a space', '_', '-', ',', '.', '&', '2'],
    )
    def test_valid_location_name(self, valid_name):
        location = Location.objects.create(name=valid_name, city=valid_name, street=valid_name,
                                           street_number=STREET_NUMBER, indoor=INDOOR,
                                           description=DESCRIPTION)
        location.full_clean()
        assert location.name == valid_name
        assert location.city == valid_name
        assert location.street == valid_name

    def test_update_location(self, location1):
        assert location1.name == LOCATION_NAME
        assert location1.city == CITY
        assert location1.street == STREET
        assert location1.street_number == STREET_NUMBER
        assert location1.indoor == INDOOR
        assert location1.description == DESCRIPTION
        location1.update(LOCATION_NAME_NEW, CITY_NEW, STREET_NEW, STREET_NUMBER_NEW,
                         INDOOR_NEW, DESCRIPTION_NEW)
        updated_location = Location.objects.get(id=location1.id)
        assert updated_location.name == LOCATION_NAME_NEW
        assert updated_location.city == CITY_NEW
        assert updated_location.street == STREET_NEW
        assert updated_location.street_number == STREET_NUMBER_NEW
        assert updated_location.indoor == INDOOR_NEW
        assert updated_location.description == DESCRIPTION_NEW

    @pytest.mark.parametrize("name, city, street, street_number, indoor, description", [
        (EMPTY_FIELD, CITY, STREET, STREET_NUMBER, INDOOR, DESCRIPTION),  # empty name
        (LOCATION_NAME, LONG_FIELD, STREET, STREET_NUMBER, INDOOR, DESCRIPTION),  # long city name
        (LOCATION_NAME, CITY, SPECIAL_CHARACTERS, STREET_NUMBER, INDOOR, DESCRIPTION),  # street name with special chars
    ],
                             )
    def test_update_of_invalid_values(self, location1, name, city, street, street_number, indoor, description):
        assert location1.name == LOCATION_NAME
        assert location1.city == CITY
        assert location1.street == STREET
        assert location1.street_number == street_number
        assert location1.indoor == indoor
        assert location1.description == description
        with pytest.raises(ValidationError):
            location1.update(name=name, city=city, street=street, street_number=street_number, indoor=indoor,
                             description=description)
