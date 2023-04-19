from django.db import models

from category.models import Category
from location.models import Location


class CategoryLocation(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['category', 'location'],
                                    name='unique category-location')
        ]

    def update(self, category=None, location=None):
        if category is not None:
            self.category = category
        if location is not None:
            self.location = location
        self.full_clean()
        self.save()
