# Generated by Django 5.1.1 on 2024-11-02 21:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_scheduleitem_category_scheduleitem_schedule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduleitem',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedule_items', to='main.schedule'),
        ),
    ]
