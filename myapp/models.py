from django.db import models
from .utils import sanitize_blog_body

# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Message(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} <{self.email}>"
    
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.body = sanitize_blog_body(self.body)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title