from django.contrib import admin
from .models import Project, Message, BlogPost

# Register your models here.
admin.site.register(Project)
admin.site.register(Message)
admin.site.register(BlogPost)