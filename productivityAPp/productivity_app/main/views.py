from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate, update_session_auth_hash
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import CreateNewTimer
from .models import PomodoroTimer  # Import your model

# Create your views here.

@login_required(login_url='/register/')
def home(response):
    return render(response, "main/home.html", {})

@login_required(login_url="/register/")
def settings(response):
    return render(response, "main/settings.html", {})


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
    return render(request, "main/productivity.html", {'timers': timers})

@login_required(login_url='/register/')
def start_timer(request, id):
    timers = PomodoroTimer.objects.filter(user=request.user)
    return render(request, "main/productivity.html", {'timers': timers})


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



@csrf_exempt
def end_pomodoro(request):
    global timer_ongoing, current_timer
    if request.method == 'POST':
        timer_ongoing = False
        current_timer = None
    return redirect('pomodoro')  # Use the URL name for redirection
