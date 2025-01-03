from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import LoginForm, CreateAccountForm
from django.contrib.auth.hashers import make_password, check_password
from .models import users
import os
import datetime
from django.views.decorators.csrf import csrf_exempt
import json

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

    response = render(request, 'index.html', context)

    # Before showing the login page, check if user has stayloggedin cookie
    if "stay_loggedin" in request.COOKIES.keys():
        uid = request.COOKIES.get("stay_loggedin", None)
        try:
            if users.objects.filter(user_id=uid).exists():
                request.session['user_id'] = uid
                return HttpResponseRedirect("/main")
            else:
                response.delete_cookie('stay_loggedin')
        except:
            response.delete_cookie('stay_loggedin')

    return response

# Function for handling login form
def login(request):
    if request.method == "POST":
        # Only POST requests are allowed
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            checkbox = form.cleaned_data["checkbox"]

            # Check if user exists in database
            if not users.objects.filter(username=username).exists():
                return HttpResponse("wrong")
            
            # Check that password is correct
            user = users.objects.get(username=username)
            if not check_password(password, user.password):
                return HttpResponse("wrong")
            
            # set session variable
            uuid_str = str(user.user_id)
            request.session['user_id'] = uuid_str

            # If user wanted to stay logged in
            response = HttpResponse("ok")
            if checkbox:
                max_age = 365 * 24 * 60 * 60  # one year
                expires = datetime.datetime.strftime(
                    datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                    "%a, %d-%b-%Y %H:%M:%S GMT",
                )
                response.set_cookie(key='stay_loggedin', value=uuid_str, max_age=max_age ,expires=expires)

            return response
        else:
            return HttpResponse("error")
    else:
        return render(request, 'error_pages/405.html')

# Function to render main page
def main(request):
    return render(request, 'main.html')

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

# function that handles creating of an account
def create_account_form_handler(request):
    if request.method == "POST":
        # Only POST requests are allowed
        form = CreateAccountForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]
            description = form.cleaned_data["description"]

            # Check if username has non english characters
            whitelist = "abcdefghijklmnopqrstuvwxyz1234567890"
            username_lower = username.lower()
            for c in username_lower:
                if c not in whitelist:
                    return HttpResponse("ascii")

            # Check if username is taken
            if users.objects.filter(username=username).exists():
                return HttpResponse("taken")
            
            # Check if email is already registered
            if users.objects.filter(email=email).exists():
                return HttpResponse("email_taken")
            
            # Check if username is only numbers
            if username.isdigit():
                return HttpResponse("numeric")

            # Hash password
            password_hash = make_password(password)

            # Get join date
            now = datetime.now()
            joindate = now.strftime("%d/%m/%Y %H:%M")

            # If description wasnt filled out, make the description be "no description"
            if not description:
                description = "No description"

            # Register user to database
            user = users(
                username=username,
                password=password_hash,
                email=email,
                joindate=joindate,
                description=description,
            )
            user.save()

            # Set session variables
            user = users.objects.get(username=username)
            uuid_str = str(user.user_id)
            request.session['user_id'] = uuid_str

            return HttpResponse("ok")
        else:
            return HttpResponse("error")
    else:
        return render(request, 'error_pages/405.html')

# Function to validate username while user is typing it in
@csrf_exempt
def username_validate(request):
    if request.method == "POST":
        # Only POST requests are allowed
        username = request.POST.get("username", "")
        validate_list = {}

        # Check if username has non english characters
        whitelist = "abcdefghijklmnopqrstuvwxyz1234567890"
        username_lower = username.lower()
        for c in username_lower:
            if c not in whitelist:
                validate_list['ascii'] = "true"
        
        # Check if username is between 5 to 30 letters
        if len(username) > 30 or len(username) < 5:
            validate_list['between_letters'] = "true"
        
        # Check if username is taken
        if users.objects.filter(username=username).exists():
            validate_list["taken"] = "true"
        
        # Check if username is only numbers
        if username.isdigit():
            validate_list["numeric"] = "true"

        return HttpResponse(json.dumps(validate_list), content_type = "application/json")
    else:
        return render(request, 'error_pages/405.html')