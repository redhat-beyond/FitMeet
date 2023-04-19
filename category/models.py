from django.db import models
from django.core.validators import RegexValidator


valid_name = RegexValidator(r'^[&0-9a-zA-Z\s_\.\,-]+$',
                            'Only alphanumeric characters, and ,.-_& are allowed.')


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True, validators=[valid_name])

    def __str__(self):
        return self.name

    def update(self, name):
        self.name = name
        self.full_clean()
        self.save()
