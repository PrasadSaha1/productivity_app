# Generated by Django 5.1.1 on 2024-10-05 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_todolist_item'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todolist',
            name='name',
            field=models.CharField(max_length=30),
        ),
    ]