from django import forms
from django.core.validators import RegexValidator

# Form for logging in from the index page
class LoginForm(forms.Form):
    username = forms.CharField(label='', max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'login-text-input'}))
    password = forms.CharField(label='', max_length=32, widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'login-text-input'}))
    checkbox = forms.BooleanField(required=False)

# Form for creating account
class CreateAccountForm(forms.Form):
    username = forms.CharField(label='', max_length=30, min_length=5, widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'create-account-text-input'}))
    nickname = forms.CharField(label='', max_length=30, min_length=5, widget=forms.TextInput(attrs={'placeholder': 'Nickname', 'class': 'create-account-text-input'}))
    email = forms.CharField(label='', max_length=40, widget=forms.EmailInput(attrs={'placeholder': 'E-mail', 'class': 'create-account-text-input'}))
    password = forms.CharField(label='', max_length=32, widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'create-account-text-input'}))
    description = forms.CharField(label='', required=False, max_length=300, widget=forms.Textarea(attrs={'placeholder': 'Description'}))
    checkbox = forms.BooleanField()

# Form for typing in email when recovering account
class AccountRecoveryForm1(forms.Form):
    email = forms.CharField(label='', max_length=40, widget=forms.EmailInput(attrs={'placeholder': 'E-mail'}))

# Form for typing in code when recovering account
class AccountRecoveryForm2(forms.Form):
    code = forms.CharField(label='', max_length=6, min_length=6, validators=[RegexValidator(r'^\d{1,10}$')], widget=forms.TextInput(attrs={'placeholder': '000000'}))

# Form for typing in new password when recovering account
class AccountRecoveryFormNewPassword(forms.Form):
    new_password = forms.CharField(label='', max_length=32, widget=forms.PasswordInput(attrs={'placeholder': 'New password'}))
    new_password_confirm = forms.CharField(label='', max_length=32, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}))

# Form for editing profile in settings
class EditProfileForm(forms.Form):
    def __init__(self, nickname, description):
        super().__init__()
        self.fields['nickname'] = forms.CharField(label='', required=False, max_length=30, min_length=5, widget=forms.TextInput(attrs={'value': nickname, 'class': 'edit-profile-nickname'}))
        self.fields['description'] = forms.CharField(label='', required=False, max_length=300, widget=forms.Textarea(attrs={'value': 'Description', 'class' : 'edit-profile-description'}), initial=description)