from __future__ import unicode_literals
from django.utils import timezone
from django.db import migrations, transaction
from django.contrib.auth.models import User
from ..models import Profile


def create_superuser(apps, schema_editor):
    with transaction.atomic():
        superuser = User(is_superuser=True, is_staff=True, username='admin', email='admin@gmail.com')
        superuser.set_password('adminPassword')
        superuser.save()
        admin_profile = Profile(
            user=superuser, date_of_birth=timezone.datetime(2020, 5, 17), phone_number='+972521234567'
        )
        admin_profile.save()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [migrations.RunPython(create_superuser)]
