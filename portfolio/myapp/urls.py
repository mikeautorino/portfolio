from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.projects, name='projects'),
    path('contact/', views.contact, name='contact'),
    path('contact/submit/', views.submit_message, name='submit_message'),
    path('contact/success/', views.message_success, name='message_success'),
    path('about/', views.about, name='about'),
    path('blog/<int:post_id>/', views.blog_post, name='blog_post'),
]