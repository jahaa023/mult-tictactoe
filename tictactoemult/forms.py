from django import forms

# Form for logging in from the index page
class LoginForm(forms.Form):
    username = forms.CharField(label='', max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'login-text-input'}))
    password = forms.CharField(label='', max_length=32, widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'login-text-input'}))
    checkbox = forms.BooleanField(required=False)

# Form for creating account
class CreateAccountForm(forms.Form):
    username = forms.CharField(label='', max_length=30, min_length=5, widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'create-account-text-input'}))
    email = forms.CharField(label='', max_length=40, widget=forms.EmailInput(attrs={'placeholder': 'E-mail', 'class': 'create-account-text-input'}))
    password = forms.CharField(label='', max_length=32, widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'create-account-text-input'}))
    description = forms.CharField(label='', required=False, max_length=300, widget=forms.Textarea(attrs={'placeholder': 'Description'}))
    checkbox = forms.BooleanField()