from django.shortcuts import render, redirect
from .forms import RegisterForm

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User


def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    current_site = get_current_site(request)

    subject = 'Activate your account'
    html_message = render_to_string('register/verification_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': uid,
        'token': token,
    })
    plain_message = strip_tags(html_message)
    from_email = 'newprasadsaha@gmail.com'
    to = user.email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login')  # Redirect to login page after successful activation
    else:
        return render(request, 'register/activation_invalid.html')  # Show invalid token message



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until email verification
            user.save()
            send_verification_email(user, request)
            return render(request, 'register/confirmation_sent.html')
    else:
        form = RegisterForm()
    return render(request, 'register/register.html', {'form': form})


