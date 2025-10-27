from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import (
    ContactMessage, CommunityMember, Subscriber, 
    Question, Answer, Comment, Topic, Space
)

# Existing forms from your current forms.py
class DeviceRegistrationForm(forms.Form):
    ieda = forms.CharField(
        max_length=64,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter 64-character IEDA'
        })
    )
    code = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter 6-digit registration code'
        })
    )

class SocialAccountForm(forms.Form):
    PLATFORM_CHOICES = [
        ('', 'Select a platform'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
    ]
    
    platform = forms.ChoiceField(
        choices=PLATFORM_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'hidden'
        })
    )

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition duration-300'
            })

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition duration-300'
            })

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your email address'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Subject of your message'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Your message...',
                'rows': 5
            }),
        }

class CommunityForm(forms.ModelForm):
    class Meta:
        model = CommunityMember
        fields = ['name', 'email', 'membership_type', 'organization', 'interests']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your email address'
            }),
            'organization': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your organization (optional)'
            }),
            'interests': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Your areas of interest or expertise...',
                'rows': 4
            }),
            'membership_type': forms.Select(attrs={
                'class': 'form-input'
            }),
        }

class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your email address'
            })
        }

# New Community Forms
class QuestionForm(forms.ModelForm):
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'topic-checkbox'
        }),
        required=False
    )

    class Meta:
        model = Question
        fields = ['title', 'content', 'topics', 'is_anonymous']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'What is your question?'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Provide details about your question...',
                'rows': 6
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['topics'].queryset = Topic.objects.filter(is_active=True)

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content', 'is_anonymous']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Write your answer...',
                'rows': 8
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Add a comment...',
                'rows': 3,
                'maxlength': 1000
            }),
        }

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Topic name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Describe this topic...',
                'rows': 3
            }),
        }

class SpaceForm(forms.ModelForm):
    class Meta:
        model = Space
        fields = ['name', 'description', 'is_public', 'topics']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Space name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Describe this space...',
                'rows': 4
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'topics': forms.SelectMultiple(attrs={
                'class': 'form-input'
            }),
        }

class CommunityMemberProfileForm(forms.ModelForm):
    class Meta:
        model = CommunityMember
        fields = ['name', 'bio', 'organization', 'location', 'website', 'profile_picture']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Tell us about yourself...',
                'rows': 4
            }),
            'organization': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your organization'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your location'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your website URL'
            }),
        }