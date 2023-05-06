from django.db import migrations


def create_initial_categories(apps, schema_editor):
    Category = apps.get_model('category', 'Category')
    Category.objects.create(name='Soccer')
    Category.objects.create(name='Football')
    Category.objects.create(name='Basketball')
    Category.objects.create(name='Baseball')
    Category.objects.create(name='Gym')
    Category.objects.create(name='Track and field')


class Migration(migrations.Migration):
    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_categories),
    ]
