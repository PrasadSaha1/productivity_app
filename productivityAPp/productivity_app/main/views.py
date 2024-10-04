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
import json

from .forms import CreateNewTimer
from .models import PomodoroTimer  # Import your model

# Create your views here.
breaks_until_long_break = -1
@login_required(login_url='/register/')
def home(response):
    return render(response, "main/home.html", {})


@login_required(login_url="/register/")
def settings(response):
    return render(response, "main/settings.html", {})


@login_required(login_url="/register/")
def logout_view(request):
    global breaks_until_long_break
    for timer in PomodoroTimer.objects.filter(user=request.user):
        timer.current_state = "inactive"
        timer.save()
    breaks_until_long_break = -1
    # Log out the user
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
            print(breaks_until_long_break)
            return render(request, "main/start_timer.html",
            {'timer': timer, 'work_sessions_left': breaks_until_long_break + 1,
             "breaks_until_long_break": breaks_until_long_break})
    return render(request, "main/productivity.html", {'timers': timers})

@login_required(login_url='/register/')
def start_timer(request, id):
    global breaks_until_long_break
    timer = PomodoroTimer.objects.get(id=id)

    if timer.current_state == "inactive":
        timer.current_state = "timer_running"
        breaks_until_long_break = timer.times_repeat - 1
        timer.save()
    return render(request, "main/start_timer.html",
                  {'timer': timer, 'work_sessions_left': breaks_until_long_break + 1,
                   "breaks_until_long_break": breaks_until_long_break})


@login_required(login_url='/register/')
def edit_timer(request, id):
    oringial_timer = PomodoroTimer.objects.get(id=id)
    date_created = str(oringial_timer.date_created)[:10]

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
            print(str(oringial_timer.date_created)[:10])
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
    global breaks_until_long_break
    for timer in PomodoroTimer.objects.filter(user=request.user):
        timer.current_state = "inactive"
        timer.save()
    breaks_until_long_break = -1
    return render(request, "main/after_end_pomodoro.html")



