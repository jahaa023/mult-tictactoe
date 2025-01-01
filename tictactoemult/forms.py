from django import forms

# Form for logging in from the index page
class LoginForm(forms.Form):
    username = forms.CharField(label='', max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(label='', max_length=32, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))