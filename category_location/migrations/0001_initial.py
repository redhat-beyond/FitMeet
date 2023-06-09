# Generated by Django 4.2 on 2023-04-26 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0001_initial'),
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='category.category')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.location')),
            ],
        ),
        migrations.AddConstraint(
            model_name='categorylocation',
            constraint=models.UniqueConstraint(fields=('category', 'location'), name='unique category-location'),
        ),
    ]
