from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


class PomodoroTimer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pomodoroTimer", null=True)
    name = models.CharField(max_length=200)
    work_period = models.IntegerField(default=-1)
    break_period = models.IntegerField(default=-1)
    times_repeat = models.IntegerField(default=-1)
    sound_on_work_end = models.BooleanField(default=False)
    sound_on_break_end = models.BooleanField(default=False)
    date_created = models.DateField(default=timezone.now)
    long_break = models.IntegerField(default=-1)
    auto_mode = models.BooleanField(default=False)
    current_state = models.CharField(default="inactive", max_length=200)
    breaks_until_long_break = models.IntegerField(default=-1)

    def __str__(self):
        return self.name


class TodoList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="todolist", null=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Item(models.Model):
    todolist = models.ForeignKey(TodoList, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    complete = models.BooleanField()

    def __str__(self):
        return self.text


class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedule", null=True)
    name = models.CharField(max_length=30)
    task_category = models.CharField(max_length=30)
    day_active = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ScheduleItem(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='schedule_items')
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=30)
    start_time = models.TimeField()
    end_time = models.TimeField()
    next_start_time = models.TimeField(default=datetime.time(9, 0))

    def __str__(self):
        return self.name




