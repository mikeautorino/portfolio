from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages as django_messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from .models import Project, Message
from .utils import is_valid_email_format, email_exists

# Create your views here.
def home(request):
    return render(request, 'home.html')

def projects(request):
    all_projects = Project.objects.all()
    return render(request, 'projects.html', {'projects': all_projects})

def contact(request):
    return render(request, 'contact.html')


@require_POST
def submit_message(request):
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    # support form field named either 'message' or 'content'
    content = request.POST.get('message', '').strip() or request.POST.get('content', '').strip()
    if not (name and email and content):
        django_messages.error(request, 'Please fill in all fields.')
        return redirect('contact')

    # Rate limiting based on client IP
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
    if not ip:
        ip = 'unknown'

    min_interval = 30  # seconds between messages from same IP
    max_per_hour = 5

    last_key = f"msg_last:{ip}"
    count_key = f"msg_count:{ip}"

    last_ts = cache.get(last_key)
    if last_ts:
        import time
        if time.time() - last_ts < min_interval:
            django_messages.error(request, 'You are sending messages too quickly. Please wait before sending another message.')
            return redirect('contact')

    count = cache.get(count_key, 0)
    if count >= max_per_hour:
        django_messages.error(request, 'Message limit reached. Try again later.')
        return redirect('contact')

    # Validate email format
    if not is_valid_email_format(email):
        django_messages.error(request, 'Please provide a valid email address.')
        return redirect('contact')

    # Verify email existence via MX/SMTP check — optional and off by default
    if getattr(settings, 'CHECK_EMAIL_EXISTENCE', False):
        exists = email_exists(email)
        if not exists:
            django_messages.error(request, 'The email address does not appear to exist. Please check and try again.')
            return redirect('contact')
    else:
        # existence check skipped
        exists = None

    # Create the message
    Message.objects.create(name=name, email=email, content=content)

    # Update rate limit counters
    cache.set(last_key, __import__('time').time(), timeout=min_interval)
    cache.incr(count_key) if cache.get(count_key) is not None else cache.set(count_key, 1, timeout=3600)

    # Send notification to site owner (best-effort)
    subject = f"New message from {name}"
    body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{content}"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@localhost'
    recipients = []
    # Prefer ADMINS setting if present
    admins = getattr(settings, 'ADMINS', None)
    if admins:
        recipients = [a[1] for a in admins]
    else:
        recipients = [getattr(settings, 'DEFAULT_FROM_EMAIL', 'mautorino101@gmail.com')]

    try:
        send_mail(subject, body, from_email, recipients, fail_silently=True)
    except Exception:
        # fail silently for email sending failures
        pass

    django_messages.success(request, 'Your message has been sent. Thank you!')
    return redirect('message_success')

def about(request):
    return render(request, 'about.html')


def message_success(request):
    return render(request, 'message_success.html')