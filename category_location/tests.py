import pytest
from django.db import IntegrityError
from .models import Location
from .models import Category
from .models import CategoryLocation


CATEGORY_NAME = "category1"
LOCATION_NAME = "location1"
CITY = "city1"
STREET = "street1"
STREET_NUMBER = 1
INDOOR = False
DESCRIPTION = "description1"

OTHER_CATEGORY_NAME = 'category2'
OTHER_LOCATION_NAME = 'location2'
OTHER_CITY = "city2"
OTHER_STREET = "street2"
OTHER_STREET_NUMBER = 2
OTHER_INDOOR = False
OTHER_DESCRIPTION = "description2"


@pytest.fixture
def category1():
    category1 = Category.objects.create(name=CATEGORY_NAME)
    category1.save()
    return category1


@pytest.fixture
def location1():
    location1 = Location.objects.create(name=LOCATION_NAME, city=CITY, street=STREET,
                                        street_number=STREET_NUMBER, indoor=INDOOR, description=DESCRIPTION)
    location1.save()
    return location1


@pytest.fixture
def category_location1(category1, location1):
    category_location1 = CategoryLocation.objects.create(category=category1, location=location1)
    category_location1.save()
    return category_location1


@pytest.mark.django_db
class TestCategoryModel:

    def test_category_location_with_same_category_and_location(self,
                                                               category_location1, category1, location1):
        assert category_location1.category == category1
        assert category_location1.location == location1
        with pytest.raises(IntegrityError):
            CategoryLocation.objects.create(category=category1, location=location1)

    def test_update_category_location(self,
                                      category_location1, category1, location1):
        assert category_location1.category == category1
        assert category_location1.location == location1
        category2 = Category.objects.create(name=OTHER_CATEGORY_NAME)
        location2 = Location.objects.create(name=OTHER_LOCATION_NAME, city=OTHER_CITY, street=OTHER_STREET,
                                            street_number=OTHER_STREET_NUMBER, indoor=OTHER_INDOOR,
                                            description=OTHER_DESCRIPTION)
        category_location1.update(category=category2, location=location2)
        category_location1 = CategoryLocation.objects.get(id=category_location1.id)
        assert category_location1.category == category2
        assert category_location1.location == location2
