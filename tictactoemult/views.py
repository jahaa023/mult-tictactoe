from django.shortcuts import render
from django.http import HttpResponse
from .forms import LoginForm, CreateAccountForm
import os

# Create your views here.

# Defines universal files (css, javascript)
static_dir = os.getcwd() + '\\tictactoemult\\static'
with open(static_dir + '\\css\\universal.css', 'r') as data:
    universal_css = data.read()
with open(static_dir + '\\js\\universal.js', 'r') as data:
    universal_js = data.read()

# Function for rendering index/login page
def index(request):
    # The default index.html page, with a form for logging in
    context = {}
    context['form'] = LoginForm()

    context['universal_css'] = universal_css
    context['universal_js'] = universal_js

    # Forces css and js file to load its contents into a style and script tag instead of a src. Kinda like php include or require.
    with open(static_dir + '\\css\\index.css', 'r') as data:
        context['index_css'] = data.read()
    with open(static_dir + '\\js\\index.js', 'r') as data:
        context['index_js'] = data.read()
    return render(request, 'index.html', context)

# Function for handling login form
def login(request):
    if request.method == "POST":
        # Only POST requests are allowed
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Check if user exists in database

            return HttpResponse("ok")
        else:
            return HttpResponse("error")
    else:
        return render(request, 'error_pages/405.html')

# Function to render main page
def main(request):
    return HttpResponse("test")

# Function to render account creation page
def create_account(request):
    context = {}
    context['form'] = CreateAccountForm()
    context['universal_css'] = universal_css
    context['universal_js'] = universal_js
    with open(static_dir + '\\css\\create_account.css', 'r') as data:
        context['create_account_css'] = data.read()
    with open(static_dir + '\\js\\create_account.js', 'r') as data:
        context['create_account_js'] = data.read()
    return render(request, 'create_account.html', context)