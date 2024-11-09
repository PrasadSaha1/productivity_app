from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate, update_session_auth_hash, logout
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.db.models import Max
import json
from datetime import datetime

from .forms import CreateNewTimer, CreateNewList, CreateNewSchedule, EditSchedule
from .models import PomodoroTimer, TodoList, Schedule, ScheduleItem

# Create your views here.
breaks_until_long_break = -1
work_time_elapsed = 0
last_work_session_length = 0

@login_required(login_url='/register/')
def home(response):
    return render(response, "main/home.html", {})


@login_required(login_url="/register/")
def settings(response):
    return render(response, "main/settings.html", {})


@login_required(login_url="/register/")
def logout_view(request):
    global breaks_until_long_break, last_work_session_length, work_time_elapsed
    for timer in PomodoroTimer.objects.filter(user=request.user):
        timer.current_state = "inactive"
        timer.save()
    breaks_until_long_break = -1
    last_work_session_length = 0
    work_time_elapsed = 0
    logout(request)

    # Redirect to a custom page that will clear localStorage
    return render(request, "main/clear_storage.html")


@login_required(login_url="/register/")
def change_username(request):
    if request.method == 'POST':
        new_username = request.POST.get('new_username')
        password = request.POST.get('password')

        if new_username and password:
            # Check if the username is already taken
            if User.objects.filter(username=new_username).exists():
                return JsonResponse({'status': 'taken'})

            # Check if the provided password is correct
            user = authenticate(request, username=request.user.username, password=password)
            if user is None:
                return JsonResponse({'status': 'incorrect_password'})

            # Change the username and save
            request.user.username = new_username
            request.user.save()
            messages.success(request, 'Username successfully changed.')
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'})
    return render(request, 'main/change_username.html')


@login_required(login_url="/register/")
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the current password is correct
        user = authenticate(request, username=request.user.username, password=current_password)
        if user is None:
            return JsonResponse({'status': 'incorrect_password'})

        # Check if the new passwords match
        if new_password != confirm_password:
            return JsonResponse({'status': 'password_mismatch'})

        # Update the password and save the user
        user.set_password(new_password)
        user.save()

        # Keep the user logged in after changing the password
        update_session_auth_hash(request, user)

        messages.success(request, 'Password successfully changed.')
        return JsonResponse({'status': 'success'})

    return render(request, "main/change_password.html", {})


@login_required(login_url='/register/')
def make_new_timer(request):
    if request.method == "POST":
        form = CreateNewTimer(request.POST)

        if form.is_valid():
            timer = form.save(commit=False)  # Save the form but don't commit yet
            timer.user = request.user  # Assign the logged-in user to the timer
            timer.save()  # Now save the timer

            # Redirect to the productivity view
            return redirect('pomodoro')  # Use the URL name for redirection
        else:
            print(form.errors)
    else:
        form = CreateNewTimer()

    current_date = timezone.now().strftime('%Y-%m-%d')
    return render(request, "main/make_new_timer.html", {'form': form, 'current_date': current_date})


@login_required(login_url='/register/')
def productivity(request):
    timers = PomodoroTimer.objects.filter(user=request.user)
    for timer in timers:
        if timer.current_state != "inactive":
            file = "main/start_timer.html"
            if timer.work_period == -1:
                file = "main/start_auto_timer.html"
            return render(request, file,
            {'timer': timer, 'work_sessions_left': breaks_until_long_break + 1,
             "breaks_until_long_break": breaks_until_long_break,
             "last_work_session_length": last_work_session_length,
             "work_time_elapsed": work_time_elapsed})
    return render(request, "main/productivity.html", {'timers': timers})

@login_required(login_url='/register/')
def start_timer(request, id):
    global breaks_until_long_break
    timer = PomodoroTimer.objects.get(id=id)

    if timer.current_state == "inactive":
        timer.current_state = "timer_running"
        breaks_until_long_break = timer.times_repeat - 1
        timer.save()

    file = "main/start_timer.html"
    if timer.work_period == -1:
        file = "main/start_auto_timer.html"

    return render(request, file,
                  {'timer': timer, 'work_sessions_left': breaks_until_long_break + 1,
                   "breaks_until_long_break": breaks_until_long_break,
                   "work_time_elapsed": work_time_elapsed,
                   "last_work_session_length": last_work_session_length})


@login_required(login_url='/register/')
def edit_timer(request, id):
    oringial_timer = PomodoroTimer.objects.get(id=id)
    date_created = str(oringial_timer.date_created)[:10]
    print(request.method)

    if request.method == "POST":
        form = CreateNewTimer(request.POST)

        if form.is_valid():
            timer = form.save(commit=False)  # Save the form but don't commit yet
            timer.user = request.user  # Assign the logged-in user to the timer
            timer.save()  # Now save the timer
            oringial_timer.delete()

            # Redirect to the productivity view
            return redirect('pomodoro')  # Use the URL name for redirection
        else:
            print(form.errors)
    else:
        form = CreateNewTimer()

    return render(request, "main/edit_timer.html", {'timer': oringial_timer, "date_created": date_created})


@login_required(login_url='/register/')
def delete_timer(request, id):
    timer = PomodoroTimer.objects.get(id=id)
    timer.delete()

    timers = PomodoroTimer.objects.filter(user=request.user)
    return render(request, "main/productivity.html", {'timers': timers})


@require_POST
@login_required(login_url="/register/")
def update_timer_state(request, id):
    timer = get_object_or_404(PomodoroTimer, id=id, user=request.user)

    # Extract the new state from the request body
    data = json.loads(request.body)
    new_state = data.get('state')

    # Update the timer's state
    if new_state:
        timer.current_state = new_state
        timer.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)

@login_required(login_url="/register/")
def update_breaks_until_long_break(request):
    global breaks_until_long_break
    if request.method == 'POST':
        new_value = request.POST.get('new_value')  # Get the value from the JavaScript request
        request.session['breaks_until_long_break'] = int(new_value)  # Update the variable
        breaks_until_long_break = int(new_value)
        return JsonResponse({'status': 'success', 'new_value': new_value})
    return JsonResponse({'status': 'failure'})

@method_decorator(csrf_exempt, name='dispatch')  # Exempt CSRF for simplicity (not recommended for production)
class UpdateTimerStateView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        new_state = data.get('state')

        # Update your timer instance here
        for timer in PomodoroTimer.objects.filter(user=request.user):
            if timer.current_state != "inactive":
                timer.current_state = new_state
                timer.save()

        return JsonResponse({'success': True, 'new_state': new_state})


@csrf_exempt
def end_pomodoro(request):
    global breaks_until_long_break, last_work_session_length, work_time_elapsed
    for timer in PomodoroTimer.objects.filter(user=request.user):
        timer.current_state = "inactive"
        timer.save()
    breaks_until_long_break = -1
    last_work_session_length = 0
    work_time_elapsed = 0
    return render(request, "main/after_end_pomodoro.html")

@login_required(login_url="/register/")
def update_work_time_elapsed(request):
    global work_time_elapsed
    if request.method == 'POST':
        new_value = request.POST.get('new_value')
        request.session['work_time_elapsed'] = int(new_value)
        work_time_elapsed = int(new_value)
        return JsonResponse({'status': 'success', 'new_value': new_value})
    return JsonResponse({'status': 'failure'})


@login_required(login_url="/register/")
def update_last_work_session_length(request):
    global last_work_session_length
    if request.method == 'POST':
        new_value = request.POST.get('new_value')
        request.session['last_work_session_length'] = int(new_value)
        last_work_session_length = int(new_value)
        return JsonResponse({'status': 'success', 'new_value': new_value})
    return JsonResponse({'status': 'failure'})

@login_required(login_url="/register/")
def todo(request):
    ls = TodoList.objects.filter(user=request.user).order_by('-id')
    return render(request, "main/todo.html", {"ls": ls})


@login_required(login_url='/register/')
def create_todo_list(request):
    if request.method == "POST":
        form = CreateNewList(request.POST)

        if form.is_valid():
            n = form.cleaned_data["name"]
            t = TodoList(name=n)
            t.save()
            request.user.todolist.add(t)

        # return redirect("/%i" % t.id)
        return HttpResponseRedirect("/view_single_list/%i" % t.id)

    else:
        form = CreateNewList()
    return render(request, "main/create_todo_list.html", {"form": form})


@login_required(login_url='/register/')
def view_single_list(request, id):
    ls = get_object_or_404(TodoList, id=id)

    if ls in request.user.todolist.all():
        if request.method == "POST":
            for item in ls.item_set.all():
                print(item)
                if request.POST.get("c" + str(item.id)) == "clicked":
                    item.delete()
                else:
                    item.complete = False
                    item.save()

            if request.POST.get("newItem"):
                txt = request.POST.get("new")
                ls.item_set.create(text=txt, complete=False)

        return render(request, "main/view_single_list.html", {"ls": ls})
    else:
        return render(request, "main/todo.html", {})

@login_required(login_url='/register/')
def scheduler(request):
    ls = Schedule.objects.filter(user=request.user).order_by('-id')

    today_schedules = []
    future_schedules = []
    past_schedules = []

    today_date = datetime.now().date()
    today_weekday = today_date.strftime("%A")

    for item in ls:
        if item.day_active.startswith(tuple("0123456789")):  # If starts with a number
            # Convert the schedule_date string into a datetime object
            try:
                schedule_date = datetime.strptime(item.day_active, "%m-%d-%Y").date()  # Adjust format as needed

                # Compare the parsed date with today's date
                if schedule_date == today_date:
                    today_schedules.append(item)
                elif schedule_date > today_date:
                    future_schedules.append(item)
                else:
                    past_schedules.append(item)
            except ValueError:
                # Handle the case where the date string is not in the expected format
                past_schedules.append(item)  # or skip, depending on your needs
        elif item.day_active == "never":
            past_schedules.append(item)
        elif today_weekday in item.day_active:
            today_schedules.append(item)
        else:
            future_schedules.append(item)

    context = {
        'today_schedules': today_schedules,
        'future_schedules': future_schedules,
        'past_schedules': past_schedules,
    }

    return render(request, 'main/scheduler.html', context)

@login_required(login_url='/register/')
def create_scheduler(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        type_days_active = request.POST.get('daysActive')
        task_categories = request.POST.getlist('task_category')
        formatted_tasks = ""
        days_active = ""
        for task in task_categories:
            formatted_tasks += task + ","

        if type_days_active == 'specific':
            specific_date = request.POST.get('specific_date')
            formatted_date = timezone.datetime.strptime(specific_date, "%Y-%m-%d").strftime("%m-%d-%Y")
            days_active = formatted_date
        elif type_days_active == 'repeating':
            selected_days = request.POST.getlist('days')
            for day in selected_days:
                days_active += f"{day.title()}, "
            days_active = days_active[:-2]

        else:  # type_days_active == 'never'
            days_active = 'never'

        # Save to the model
        Schedule.objects.create(name=name, day_active=days_active, user=request.user, task_category=formatted_tasks)

        highest_schedule_id = Schedule.objects.aggregate(Max('id'))['id__max']
        schedule = get_object_or_404(Schedule, id=highest_schedule_id)
        print(schedule.task_category)
        return render(request, 'main/view_single_schedule.html', {"schedule": schedule})
    else:
        form = CreateNewSchedule()

    return render(request, 'main/create_scheduler.html')


@login_required(login_url='/register/')
def edit_schedule(request, id):
    schedule = Schedule.objects.get(id=id)
    if request.method == "POST":
        name = request.POST.get('name')
        type_days_active = request.POST.get('daysActive')
        task_categories = request.POST.getlist('task_category')
        formatted_tasks = ""
        days_active = ""
        for task in task_categories:
            formatted_tasks += task + ","

        if type_days_active == 'specific':
            specific_date = request.POST.get('specific_date')
            formatted_date = timezone.datetime.strptime(specific_date, "%Y-%m-%d").strftime("%m-%d-%Y")
            days_active = formatted_date
        elif type_days_active == 'repeating':
            selected_days = request.POST.getlist('days')
            for day in selected_days:
                days_active += f"{day.title()}, "
            days_active = days_active[:-2]
        else:  # type_days_active == 'never'
            days_active = 'never'

        # POST doesn't work the way it should
        if name:
            max_id = Schedule.objects.aggregate(Max('id'))['id__max']
            new_id = (max_id + 1) if max_id is not None else 1  # Handle case where there are no entries
            Schedule.objects.filter(id=id).update(name=name, day_active=days_active, task_category=formatted_tasks)

            for task in schedule.schedule_items.all():
                if task.category not in schedule.task_category:
                    task.category = "No Category"
                    task.save()

            return render(request, 'main/view_single_schedule.html', {"schedule": schedule})

    return render(request, 'main/edit_schedule.html', {"schedule": schedule})


@login_required(login_url='/register/')
def delete_schedule(request, id):
    schedule = Schedule.objects.get(id=id)
    schedule.delete()
    return redirect('scheduler')


@login_required(login_url='/register/')
def view_single_schedule(request, id):
    schedule = get_object_or_404(Schedule, id=id)
    print(schedule.task_category)
    return render(request, "main/view_single_schedule.html", {"schedule": schedule})


@login_required(login_url='/register/')
def modify_schedule(request, id):
    schedule = get_object_or_404(Schedule, id=id)
    categories = schedule.task_category
    categories = categories.split(",")
    print(categories)

    if request.method == "POST":
        # Delete all existing schedule items for this schedule
        schedule.schedule_items.all().delete()

        categories = request.POST.get("categories", "")
        names = request.POST.get("names", "")
        start_times = request.POST.get("start_times", "")
        end_times = request.POST.get("end_times", "")

        categories_split = categories.split(",")
        names_split = names.split(",")
        start_times_split = start_times.split(",")
        end_times_split = end_times.split(",")

        for i in range(len(categories_split)):
            if i == len(categories_split) - 1:
                next_start_time = end_times_split[i]
            else:
                next_start_time = start_times_split[i + 1]

            schedule.schedule_items.create(
                name=names_split[i],
                category=categories_split[i],
                start_time=start_times_split[i],
                end_time=end_times_split[i],
                next_start_time=next_start_time
            )
        print(schedule.task_category)
        return render(request, "main/view_single_schedule.html", {"schedule": schedule, "categories": categories})

    return render(request, "main/modify_schedule.html", {"schedule": schedule, "categories": categories})