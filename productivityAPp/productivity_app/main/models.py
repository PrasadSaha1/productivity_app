from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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

    def __str__(self):
        return self.name
