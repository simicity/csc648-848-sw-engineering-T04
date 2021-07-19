from django import forms
from study_app.models import *

class RegistrationForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=40,
        required=True
    )
    email = forms.EmailField(
        label='Email',
        max_length=100,
        required=True
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        max_length=100,
        required=True
    )
    confirmPassword = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(),
        max_length=100,
        required=True
    )
    avatar = forms.ImageField(
        label='Avatar',
        required=False
    )
    tosCheck = forms.NullBooleanField(
        label='I agree to Terms of Service',
        widget=forms.CheckboxInput()
    )


class UserProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'avatar']


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        max_length=100,
        required=True
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        max_length=100,
        required=True
    )


class ContactForm(forms.Form):
    fullname = forms.CharField(
        label='Full Name',
        max_length=45,
        required=True
    )
    telephone = forms.CharField(
        label='Telephone',
        max_length=15,
        required=True
    )
    email = forms.EmailField(
        label='Email',
        max_length=45,
        required=True
    )
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(),
        max_length=200,
        required=True
    )


class StudyGroupForm(forms.ModelForm):
    groupName = forms.CharField(
        label='Study Group Name', 
        max_length = 100, 
        required=True
    )
    description = forms.CharField(
        label='Description',
        widget=forms.Textarea(),
        max_length = 5000,
        required=True
    )

    class Meta:
        model = StudyGroup
        fields = ['groupName', 'description']


class MainPostForm(forms.ModelForm):
    post = forms.CharField(
        widget=forms.Textarea(),
    )

    class Meta:
        model = MainPost
        fields = ['postTitle', 'post']


class MainCommentForm(forms.ModelForm):
    comment = forms.CharField(
        widget=forms.Textarea(),
    )

    class Meta:
        model = MainComment
        fields = ['comment']


class StudyGroupPostForm(forms.ModelForm):
    post = forms.CharField(
        widget=forms.Textarea(),
    )

    class Meta:
        model = StudyGroupPost
        fields = ['postTitle', 'post']


class StudyGroupCommentForm(forms.ModelForm):
    comment = forms.CharField(
        widget=forms.Textarea(),
    )

    class Meta:
        model = StudyGroupComment
        fields = ['comment']


class MessageForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(),
    )

    class Meta:
        model = Message
        fields = ['message']
