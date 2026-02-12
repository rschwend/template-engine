from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import MasterTemplate


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class MasterTemplateForm(forms.ModelForm):
    class Meta:
        model = MasterTemplate
        fields = ("name", "subject", "body")
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Template Name",
            }),
            "subject": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Subject with {{variables}}",
            }),
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 10,
                "placeholder": "Body text with {{variables}}...",
            }),
        }
