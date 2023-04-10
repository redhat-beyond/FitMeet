from django.db import models


class Teams(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self) -> str:
        return self.name
