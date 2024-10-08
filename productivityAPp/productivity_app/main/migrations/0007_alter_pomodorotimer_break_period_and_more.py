# Generated by Django 5.1.1 on 2024-09-28 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_pomodorotimer_auto_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pomodorotimer',
            name='break_period',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='pomodorotimer',
            name='long_break',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='pomodorotimer',
            name='times_repeat',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='pomodorotimer',
            name='work_period',
            field=models.IntegerField(default=-1),
        ),
    ]
