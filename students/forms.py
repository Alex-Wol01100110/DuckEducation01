from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from courses.models import Course


class CourseEnrollForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(),
                                    widget=forms.HiddenInput)

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, 
                                 required=False, 
                                 help_text='Optional')
    last_name = forms.CharField(max_length=30, 
                                required=False, 
                                help_text='Optional')
    email = forms.EmailField(max_length=254, 
                             help_text='Enter a valid email address')

    class Meta:
        model = User
        fields = [
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'password1', 
            'password2', 
            ]

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            return email

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('This email address is already in use.')

class ResendActivationEmailForm(forms.Form):
    """Send anoter email with activation link."""
    email = forms.EmailField(max_length=254, 
                             help_text='Enter a valid email address')
                             
    class Meta:
        model = User
        fields = ['email',]

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')
        
        # Check to see if any users already exist with this email as a username.
        try:
            user_match = User.objects.get(email=email)
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            raise forms.ValidationError("There's no account with the email \
                                        you provided.")
        else:
            if user_match.profile.email_confirmed == True:
                raise forms.ValidationError("This account is active")
            else:
                return email

