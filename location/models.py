from django.db import models
from django.core.validators import RegexValidator

valid_name = RegexValidator(r'^[&0-9a-zA-Z\s_\.\,-]+$',
                            'Only alphanumeric characters, and ,.-_& are allowed.')


class Location(models.Model):
    name = models.CharField(max_length=40, unique=True, validators=[valid_name])
    city = models.CharField(max_length=20, validators=[valid_name])
    street = models.CharField(max_length=20, validators=[valid_name])
    street_number = models.PositiveIntegerField()
    indoor = models.BooleanField()
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def update(self, name=None, city=None, street=None, street_number=None, indoor=None, description=None):
        if name is not None:
            self.name = name
        if city is not None:
            self.city = city
        if street is not None:
            self.street = street
        if street_number is not None:
            self.street_number = street_number
        if indoor is not None:
            self.indoor = indoor
        if description is not None:
            self.description = description
        self.full_clean()
        self.save()
