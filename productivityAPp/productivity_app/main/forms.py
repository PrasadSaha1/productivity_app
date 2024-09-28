from django import forms
from .models import PomodoroTimer


class CreateNewTimer(forms.ModelForm):
    class Meta:
        model = PomodoroTimer
        fields = ['name', 'work_period', 'break_period', 'times_repeat',
                  'sound_on_work_end', 'sound_on_break_end', 'date_created']

