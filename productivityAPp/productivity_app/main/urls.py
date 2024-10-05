from django.urls import path

from . import views
from register import views as v

urlpatterns = [
     path("home/", views.home, name="home"),
     path("", views.home, name="home"),
     path("settings/", views.settings, name="settings"),
     path("change_username", views.change_username, name="change_username"),
     path("change_password", views.change_password, name="change_password"),
     path("make_new_timer", views.make_new_timer, name="make_new_timer"),
     path("pomodoro", views.productivity, name="pomodoro"),
     path("start_timer/<int:id>/", views.start_timer, name="start_timer"),
     path("edit_timer/<int:id>/", views.edit_timer, name="edit_timer"),
     path("delete_timer/<int:id>/", views.delete_timer, name="delete_timer"),
     path("logout_view", views.logout_view, name="logout_view"),
     path('end_pomodoro/', views.end_pomodoro, name='end_pomodoro'),
     path('update-timer-state/', views.UpdateTimerStateView.as_view(), name='update_timer_state'),
     path('update_timer_state/<int:timer_id>/', views.update_timer_state, name='update_timer_state'),
     path('update-breaks/', views.update_breaks_until_long_break, name='update_breaks_until_long_break'),
     path("update_work_time_elapsed/", views.update_work_time_elapsed, name="update_work_time_elapsed"),
     path("update_last_work_session_length/", views.update_last_work_session_length, name="update_last_work_session_length"),
     path('start_auto_timer/<int:id>', views.start_timer, name="start_auto_timer"),
     path("todo/", views.todo, name="todo"),
     path("create_todo_list/", views.create_todo_list, name="create_todo_list"),
     path('view_single_list/<int:id>', views.view_single_list, name="view_single_list"),
]
