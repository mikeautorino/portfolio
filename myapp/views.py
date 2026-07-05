from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages as django_messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from .models import Project, Message, BlogPost
from .utils import is_valid_email_format

# Create your views here.
def home(request):
    all_blog_posts = BlogPost.objects.all()
    return render(request, 'home.html', {'blog_posts': all_blog_posts})

def projects(request):
    all_projects = Project.objects.all()
    return render(request, 'projects.html', {'projects': all_projects})

def contact(request):
    form = ContactForm()
    return render(request, 'contact.html', {'form': form})


@require_POST
def submit_message(request):
    post_data = request.POST.copy()
    if not post_data.get('message') and post_data.get('content'):
        post_data['message'] = post_data.get('content')

    form = ContactForm(post_data)
    if not form.is_valid():
        django_messages.error(request, 'Please complete the form and verify the captcha.')
        return redirect('contact')

    name = form.cleaned_data['name'].strip()
    email = form.cleaned_data['email'].strip()
    content = form.cleaned_data['message'].strip()

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

    django_messages.success(request, 'Thank you for your message. I will respond as soon as possible.')
    return redirect('contact')

def about(request):
    return render(request, 'about.html')


def message_success(request):
    return render(request, 'message_success.html')


def blog_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    return render(request, 'blog_post.html', {'post': post})

def services(request):
    return render(request, 'services.html')
