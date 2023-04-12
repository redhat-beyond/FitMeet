from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateTimeField()
    phone_number = models.CharField(max_length=15)
    image_url = models.URLField(max_length=200, blank=True)
