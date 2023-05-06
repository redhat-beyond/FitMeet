import string
import re
import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import Category

CATEGORY_NAME = "category1"
CATEGORY_NAME_NEW = "category2"
LONG_NAME = "a" * 25
EMPTY_NAME = ''
SPECIAL_CHARACTERS = re.sub("[&_.,-]", "", string.punctuation)


@pytest.fixture
def category1():
    category1 = Category.objects.create(name=CATEGORY_NAME)
    category1.save()
    return category1


@pytest.mark.django_db
class TestCategoryModel:

    def test_update_category(self, category1):
        assert category1.name == CATEGORY_NAME
        category1.update(CATEGORY_NAME_NEW)
        updated_category = Category.objects.get(id=category1.id)
        assert updated_category.name == CATEGORY_NAME_NEW

    @pytest.mark.parametrize(
        "invalid_name",
        [EMPTY_NAME, LONG_NAME, SPECIAL_CHARACTERS],
    )
    def test_update_category_with_invalid_name(self, category1, invalid_name):
        assert category1.name == CATEGORY_NAME
        with pytest.raises(ValidationError):
            category1.update(invalid_name)

    def test_category_with_same_name(self, category1):
        with pytest.raises(IntegrityError):
            Category.objects.create(name=CATEGORY_NAME)

    @pytest.mark.parametrize(
        "invalid_name",
        [EMPTY_NAME, LONG_NAME, SPECIAL_CHARACTERS],
    )
    def test_create_category_with_invalid_name(self, invalid_name):
        with pytest.raises(ValidationError):
            Category.objects.create(name=invalid_name).full_clean()

    @pytest.mark.parametrize(
        "valid_name",
        ['b1', 'B', 'a space', '_', '-', ',', '.', '&'],
    )
    def test_create_category_with_valid_name(self, valid_name):
        category = Category.objects.create(name=valid_name)
        category.full_clean()
        assert category.name == valid_name

    def test_static_category(self):
        category = Category.objects.filter(name="Soccer").first()
        assert category.name == "Soccer"
