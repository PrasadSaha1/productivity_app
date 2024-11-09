# Generated by Django 5.1.1 on 2024-09-21 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pomodorotimer',
            name='sound_on_break_end',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pomodorotimer',
            name='sound_on_work_end',
            field=models.BooleanField(default=False),
        ),
    ]