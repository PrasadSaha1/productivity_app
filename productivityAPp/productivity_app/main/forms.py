from django import forms
from .models import PomodoroTimer


class CreateNewTimer(forms.ModelForm):
    class Meta:
        model = PomodoroTimer
        fields = ['name', 'work_period', 'break_period', 'times_repeat', 'sound_on_work_end',
                  'sound_on_break_end', 'date_created', 'long_break', 'auto_mode', 'current_state']

    def clean(self):
        cleaned_data = super().clean()
        auto_mode = cleaned_data.get('auto_mode', False)

        # If auto_mode is enabled, set default values
        if auto_mode:
            cleaned_data['work_period'] = -1
            cleaned_data['break_period'] = -1
            cleaned_data['times_repeat'] = -1
            cleaned_data['long_break'] = -1

        return cleaned_data