from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import PomodoroTimer
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_default_timer(sender, instance, created, **kwargs):
    if created:
        PomodoroTimer.objects.create(
            user=instance,
            name="Pomodoro Example (with auto mode)",
            auto_mode=True,
            work_period=-1,  # Default work period
            break_period=-1,  # Default break period
            times_repeat=-1,  # Default times to repeat
            long_break=-1,
            sound_on_work_end=False,  # Default sound settings
            sound_on_break_end=True,
        )
        # Create a default timer for the new user
        PomodoroTimer.objects.create(
            user=instance,
            name="Pomodoro Example (without auto mode)",
            auto_mode=False,
            work_period=25,  # Default work period
            break_period=5,  # Default break period
            times_repeat=4,  # Default times to repeat
            long_break=30,
            sound_on_work_end=True,  # Default sound settings
            sound_on_break_end=True,
        )
