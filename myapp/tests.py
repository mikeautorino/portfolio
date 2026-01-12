from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.contrib.auth.models import User
from .models import Project, Message, BlogPost
import time


class ProjectModelTest(TestCase):
    """Test cases for the Project model"""
    
    def setUp(self):
        """Create a test project"""
        self.project = Project.objects.create(
            title="Test Project",
            description="This is a test project",
            link="https://example.com"
        )
    
    def test_project_creation(self):
        """Test that a project can be created"""
        self.assertEqual(self.project.title, "Test Project")
        self.assertEqual(self.project.description, "This is a test project")
        self.assertEqual(self.project.link, "https://example.com")
    
    def test_project_str_method(self):
        """Test the __str__ method returns the title"""
        self.assertEqual(str(self.project), "Test Project")
    
    def test_project_created_at(self):
        """Test that created_at is set automatically"""
        self.assertIsNotNone(self.project.created_at)
    
    def test_project_link_blank(self):
        """Test that link field can be blank"""
        project = Project.objects.create(
            title="Project No Link",
            description="A project without a link"
        )
        self.assertEqual(project.link, "")


class MessageModelTest(TestCase):
    """Test cases for the Message model"""
    
    def setUp(self):
        """Create a test message"""
        self.message = Message.objects.create(
            name="John Doe",
            email="john@example.com",
            content="This is a test message"
        )
    
    def test_message_creation(self):
        """Test that a message can be created"""
        self.assertEqual(self.message.name, "John Doe")
        self.assertEqual(self.message.email, "john@example.com")
        self.assertEqual(self.message.content, "This is a test message")
    
    def test_message_str_method(self):
        """Test the __str__ method returns formatted string"""
        expected = "Message from John Doe <john@example.com>"
        self.assertEqual(str(self.message), expected)
    
    def test_message_sent_at(self):
        """Test that sent_at is set automatically"""
        self.assertIsNotNone(self.message.sent_at)


class BlogPostModelTest(TestCase):
    """Test cases for the BlogPost model"""
    
    def setUp(self):
        """Create a test blog post"""
        self.blog_post = BlogPost.objects.create(
            title="Test Blog Post",
            body="This is a test blog post content"
        )
    
    def test_blog_post_creation(self):
        """Test that a blog post can be created"""
        self.assertEqual(self.blog_post.title, "Test Blog Post")
        self.assertEqual(self.blog_post.body, "This is a test blog post content")
    
    def test_blog_post_str_method(self):
        """Test the __str__ method returns the title"""
        self.assertEqual(str(self.blog_post), "Test Blog Post")
    
    def test_blog_post_published_at(self):
        """Test that published_at is set automatically"""
        self.assertIsNotNone(self.blog_post.published_at)


class HomeViewTest(TestCase):
    """Test cases for the home view"""
    
    def setUp(self):
        """Create test data and client"""
        self.client = Client()
        self.blog_post = BlogPost.objects.create(
            title="Test Post",
            body="Test content"
        )
    
    def test_home_view_status_code(self):
        """Test that home view returns 200 status code"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_home_view_template(self):
        """Test that home view uses correct template"""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')
    
    def test_home_view_context(self):
        """Test that home view passes blog posts in context"""
        response = self.client.get(reverse('home'))
        self.assertIn('blog_posts', response.context)
        self.assertEqual(len(response.context['blog_posts']), 1)
        self.assertEqual(response.context['blog_posts'][0].title, "Test Post")


class ProjectsViewTest(TestCase):
    """Test cases for the projects view"""
    
    def setUp(self):
        """Create test data and client"""
        self.client = Client()
        self.project = Project.objects.create(
            title="Test Project",
            description="Test description",
            link="https://example.com"
        )
    
    def test_projects_view_status_code(self):
        """Test that projects view returns 200 status code"""
        response = self.client.get(reverse('projects'))
        self.assertEqual(response.status_code, 200)
    
    def test_projects_view_template(self):
        """Test that projects view uses correct template"""
        response = self.client.get(reverse('projects'))
        self.assertTemplateUsed(response, 'projects.html')
    
    def test_projects_view_context(self):
        """Test that projects view passes projects in context"""
        response = self.client.get(reverse('projects'))
        self.assertIn('projects', response.context)
        self.assertEqual(len(response.context['projects']), 1)
        self.assertEqual(response.context['projects'][0].title, "Test Project")


class ContactViewTest(TestCase):
    """Test cases for the contact view"""
    
    def setUp(self):
        """Create test client"""
        self.client = Client()
    
    def test_contact_view_status_code(self):
        """Test that contact view returns 200 status code"""
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
    
    def test_contact_view_template(self):
        """Test that contact view uses correct template"""
        response = self.client.get(reverse('contact'))
        self.assertTemplateUsed(response, 'contact.html')


class SubmitMessageViewTest(TestCase):
    """Test cases for the submit_message view"""
    
    def setUp(self):
        """Create test client and clear cache"""
        self.client = Client()
        cache.clear()
    
    def tearDown(self):
        """Clear cache after each test"""
        cache.clear()
    
    def test_submit_message_valid(self):
        """Test submitting a valid message"""
        response = self.client.post(reverse('submit_message'), {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'This is a test message'
        })
        
        # Should redirect to message_success
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('message_success'))
        
        # Message should be created in database
        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.first()
        self.assertEqual(message.name, 'John Doe')
        self.assertEqual(message.email, 'john@example.com')
        self.assertEqual(message.content, 'This is a test message')
    
    def test_submit_message_missing_name(self):
        """Test submitting message without name"""
        response = self.client.post(reverse('submit_message'), {
            'name': '',
            'email': 'john@example.com',
            'message': 'This is a test message'
        })
        
        # Should redirect to contact
        self.assertRedirects(response, reverse('contact'))
        
        # No message should be created
        self.assertEqual(Message.objects.count(), 0)
    
    def test_submit_message_missing_email(self):
        """Test submitting message without email"""
        response = self.client.post(reverse('submit_message'), {
            'name': 'John Doe',
            'email': '',
            'message': 'This is a test message'
        })
        
        # Should redirect to contact
        self.assertRedirects(response, reverse('contact'))
        
        # No message should be created
        self.assertEqual(Message.objects.count(), 0)
    
    def test_submit_message_missing_content(self):
        """Test submitting message without content"""
        response = self.client.post(reverse('submit_message'), {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': ''
        })
        
        # Should redirect to contact
        self.assertRedirects(response, reverse('contact'))
        
        # No message should be created
        self.assertEqual(Message.objects.count(), 0)
    
    def test_submit_message_invalid_email_format(self):
        """Test submitting message with invalid email format"""
        response = self.client.post(reverse('submit_message'), {
            'name': 'John Doe',
            'email': 'not-a-valid-email',
            'message': 'This is a test message'
        })
        
        # Should redirect to contact
        self.assertRedirects(response, reverse('contact'))
        
        # No message should be created
        self.assertEqual(Message.objects.count(), 0)
    
    def test_submit_message_rate_limiting(self):
        """Test rate limiting - messages too close together"""
        # First message should succeed
        response1 = self.client.post(reverse('submit_message'), {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'First message'
        })
        self.assertRedirects(response1, reverse('message_success'))
        
        # Second message immediately after should fail (rate limited)
        response2 = self.client.post(reverse('submit_message'), {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Second message'
        })
        self.assertRedirects(response2, reverse('contact'))
        
        # Only first message should be in database
        self.assertEqual(Message.objects.count(), 1)
    
    def test_submit_message_requires_post(self):
        """Test that submit_message view requires POST method"""
        response = self.client.get(reverse('submit_message'))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_submit_message_content_field_alternative(self):
        """Test submitting message using 'content' field instead of 'message'"""
        response = self.client.post(reverse('submit_message'), {
            'name': 'John Doe',
            'email': 'john@example.com',
            'content': 'This is a test using content field'
        })
        
        # Should succeed
        self.assertRedirects(response, reverse('message_success'))
        
        # Message should be created
        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.first()
        self.assertEqual(message.content, 'This is a test using content field')


class AboutViewTest(TestCase):
    """Test cases for the about view"""
    
    def setUp(self):
        """Create test client"""
        self.client = Client()
    
    def test_about_view_status_code(self):
        """Test that about view returns 200 status code"""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
    
    def test_about_view_template(self):
        """Test that about view uses correct template"""
        response = self.client.get(reverse('about'))
        self.assertTemplateUsed(response, 'about.html')
