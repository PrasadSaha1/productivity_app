from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import PomodoroTimer
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_out

@receiver(user_logged_out)
def handle_user_logged_out(sender, request, user, **kwargs):
    global current_timer, timer_ongoing
    print("hi")
    current_timer = None
    timer_ongoing = False

@receiver(post_save, sender=User)
def create_default_timer(sender, instance, created, **kwargs):
    if created:
        # Create a default timer for the new user
        PomodoroTimer.objects.create(
            user=instance,
            name="Pomodoro Example",
            work_period=25,  # Default work period
            break_period=5,  # Default break period
            times_repeat=4,  # Default times to repeat
            sound_on_work_end=True,  # Default sound settings
            sound_on_break_end=True,
        )
