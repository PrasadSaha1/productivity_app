from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PomodoroTimer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pomodoroTimer", null=True)
    name = models.CharField(max_length=200)
    work_period = models.IntegerField()
    break_period = models.IntegerField()
    times_repeat = models.IntegerField()
    sound_on_work_end = models.BooleanField(default=False)
    sound_on_break_end = models.BooleanField(default=False)
    date_created = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name
