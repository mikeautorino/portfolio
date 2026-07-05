from django import forms
from django.conf import settings
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3


class TestableReCaptchaField(ReCaptchaField):
    widget = ReCaptchaV3

    def validate(self, value):
        if getattr(settings, 'RECAPTCHA_TESTING', False):
            return
        super().validate(value)


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    captcha = TestableReCaptchaField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'message':
                field.widget.attrs.update({'rows': '4'})
            if field_name == 'captcha':
                field.widget.attrs.update({'class': 'g-recaptcha', 'data-action': 'contact_form'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
