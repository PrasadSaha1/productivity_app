# Generated by Django 5.1.1 on 2024-09-28 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_pomodorotimer_long_break'),
    ]

    operations = [
        migrations.AddField(
            model_name='pomodorotimer',
            name='auto_mode',
            field=models.BooleanField(default=False),
        ),
    ]