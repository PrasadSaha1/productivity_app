# Generated by Django 5.1.1 on 2024-09-21 16:34

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_pomodorotimer_sound_on_break_end_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pomodorotimer',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
