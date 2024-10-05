from django.contrib import admin
from .models import PomodoroTimer
from .models import TodoList

# Register your models here.
admin.site.register(PomodoroTimer)
admin.site.register(TodoList)