from django.shortcuts import render, get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from .forms import LoginForm, CreateAccountForm, AccountRecoveryForm1, AccountRecoveryForm2, AccountRecoveryFormNewPassword, PersonalInformationEmail
from django.contrib.auth.hashers import make_password, check_password
from .models import users, recovery_codes
import os
import datetime
import time
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
import json
from .mail import send_mail
import random
import base64
from colorthief import ColorThief

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

    # Check if temp sessipn variables are set and delete them
    if 'temp_recovery_email' in request.session:
        del request.session["temp_recovery_email"]
    
    if 'temp_recovery_uid' in request.session:
        del request.session["temp_recovery_uid"]

    # Before showing the login page, check if user has stayloggedin cookie
    if "stay_loggedin" in request.COOKIES.keys():
        token = request.COOKIES.get("stay_loggedin", None)
        try:
            if users.objects.filter(stayloggedin_token=token).exists():
                user = users.objects.get(stayloggedin_token=token)
                uuid_str = str(user.user_id)
                request.session['user_id'] = uuid_str
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
                token = str(user.stayloggedin_token)
                max_age = 365 * 24 * 60 * 60  # one year
                expires = datetime.strftime(
                    datetime.now() + timedelta(seconds=max_age),
                    "%a, %d-%b-%Y %H:%M:%S GMT",
                )
                response.set_cookie(key='stay_loggedin', value=token, max_age=max_age ,expires=expires)

            return response
        else:
            return HttpResponse("error")
    else:
        return render(request, 'error_pages/405.html')

# Function to render main page
def main(request):
    # If user is not logged in, redirect them
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")

    context = {}
    context['universal_css'] = universal_css
    context['universal_js'] = universal_js
    with open(static_dir + '\\css\\main.css', 'r') as data:
        context['main_css'] = data.read()
    with open(static_dir + '\\js\\main.js', 'r') as data:
        context['main_js'] = data.read()

    # Get information about user for things like profilepic, username etc
    user_id = request.session.get("user_id")
    if users.objects.filter(user_id=user_id).exists():
        user = users.objects.get(user_id=user_id)
        context["user"] = user
    else:
        # If user_id is not valid, force user to log in again
        request.session.flush()
        response = HttpResponseRedirect("/")
        # Delete stayloggedin cookie if it is set
        if "stay_loggedin" in request.COOKIES.keys():
            response.delete_cookie('stay_loggedin')
        # Redirect to login page
        return response

    return render(request, 'main.html', context)

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
            nickname = form.cleaned_data["nickname"]
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
                nickname=nickname,
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

# Function that renders account recovery page
def account_recovery(request):
    context = {}
    context['form'] = AccountRecoveryForm1()
    context['universal_css'] = universal_css
    context['universal_js'] = universal_js
    with open(static_dir + '\\css\\account-recovery.css', 'r') as data:
        context['account_recovery_css'] = data.read()
    with open(static_dir + '\\js\\account_recovery.js', 'r') as data:
        context['account_recovery_js'] = data.read()
    return render(request, 'account_recovery.html', context)

# Function that handles form for inputting email when recovering account
def account_recovery_email(request):
    if request.method == "POST":
        # Only POST requests are allowed
        form = AccountRecoveryForm1(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            # Check if email is registered
            if not users.objects.filter(email=email).exists():
                return HttpResponse("not_registered")

            # Generate recovery code
            recovery_code = random.randint(111111, 999999)

            # Set a expiration in unix time
            unix_now = int(time.time())
            expire = unix_now + (60 * 15) # 15 minutes

            # Send email
            mail_status = send_mail(email, "Tic Tac Toe - Recovery code", "Hi " + email + ". Your recovery code is: " + str(recovery_code))
            if mail_status == "error":
                return HttpResponse("error")

            # Insert temporary recovery code inside database
            code = recovery_codes(
                email = email,
                recovery_code=recovery_code,
                expire=expire
            )

            code.save()

            # Save email in session variable
            request.session['temp_recovery_email'] = email

            return HttpResponse("ok")
        else:
            return HttpResponse("error")
    else:
        return render(request, 'error_pages/405.html')

def account_recovery_inputcode(request):
    # Check if temp_recovery_email session variable is set
    if 'temp_recovery_email' not in request.session:
        return HttpResponseRedirect("/")
    context = {}
    context['form'] = AccountRecoveryForm2()
    context['universal_css'] = universal_css
    context['universal_js'] = universal_js
    with open(static_dir + '\\css\\account-recovery.css', 'r') as data:
        context['account_recovery_css'] = data.read()
    with open(static_dir + '\\js\\account_recovery.js', 'r') as data:
        context['account_recovery_js'] = data.read()
    return render(request, 'account_recovery/account_recovery_inputcode.html', context)

# Function that handles form for inputting code when recovering account
def account_recovery_code(request):
    if request.method == "POST":
        # Only POST requests are allowed
        form = AccountRecoveryForm2(request.POST)

        if form.is_valid():
            code = form.cleaned_data["code"]

            # Check if code is integer
            try:
                code = int(code)
            except:
                return("error")

            # Delete expired codes
            unix_now = int(time.time())
            recovery_codes.objects.filter(expire__lt=unix_now).delete()

            # Check that recovery email session variable exists
            if 'temp_recovery_email' not in request.session:
                return HttpResponse("error")

            # Check if code exists in database
            email = request.session.get('temp_recovery_email')
            if not recovery_codes.objects.filter(recovery_code=code, email=email).exists():
                return HttpResponse("expired_notfound")

            # Get user id of user with that email
            user = users.objects.get(email=email)
            uuid_str = str(user.user_id)
            request.session['temp_recovery_uid'] = uuid_str

            return HttpResponse("ok")
        else:
            return HttpResponse("error")
    else:
        return render(request, 'error_pages/405.html')

# Function to render page for the final step of account recovery
def account_recovery_final(request):
    context = {}
    context["form"] = AccountRecoveryFormNewPassword()
    context['universal_css'] = universal_css
    context['universal_js'] = universal_js
    with open(static_dir + '\\css\\account-recovery.css', 'r') as data:
        context['account_recovery_css'] = data.read()
    with open(static_dir + '\\js\\account_recovery.js', 'r') as data:
        context['account_recovery_js'] = data.read()

    # Get temporary user id
    if 'temp_recovery_uid' not in request.session:
        return HttpResponseRedirect("/")
    uid = request.session.get('temp_recovery_uid')

    # Get username attached to user id
    user = users.objects.get(user_id=uid)
    context["username"] = user.username

    return render(request, 'account_recovery/account_recovery_final.html', context)

# Function that handles form for resetting password
def reset_password(request):
    if request.method == "POST":
        # Only POST requests are allowed
        form = AccountRecoveryFormNewPassword(request.POST)

        if form.is_valid():
            new_password = form.cleaned_data["new_password"]
            new_password_confirm = form.cleaned_data["new_password_confirm"]

            # Check if passwords match
            if not new_password == new_password_confirm:
                return HttpResponse("no_match")

            # Get temporary user id
            if 'temp_recovery_uid' not in request.session:
                return HttpResponse("error")
            uid = request.session.get('temp_recovery_uid')

            # Check if new password is the same as old password
            user = users.objects.get(user_id=uid)
            old_password_hash = user.password

            if check_password(new_password, old_password_hash):
                return HttpResponse("same")

            # Hash new password and save it
            password_hash = make_password(new_password)

            user.password = password_hash
            user.save()

            return HttpResponse("ok")
        else:
            return HttpResponse("error")
    else:
        return render(request, 'error_pages/405.html')

# Logs the user out
def logout(request):
    # Remove all session variables
    request.session.flush()

    response = HttpResponseRedirect("/")

    # Delete stayloggedin cookie if it is set
    if "stay_loggedin" in request.COOKIES.keys():
        response.delete_cookie('stay_loggedin')

    # Redirect to login page
    return response

# Renders settings page
def settings(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")
    
    context = {}

    # Get user info to display
    user_id = request.session.get("user_id")
    user = users.objects.get(user_id=user_id)
    context["user"] = user

    context['universal_css'] = universal_css
    context['universal_js'] = universal_js
    with open(static_dir + '\\css\\settings.css', 'r') as data:
        context['settings_css'] = data.read()
    with open(static_dir + '\\js\\settings.js', 'r') as data:
        context['settings_js'] = data.read()

    return render(request, 'settings.html', context)

# renders page for editing profile in user settings
def edit_profile(request):
    context = {}

    # Get user info to display
    user_id = request.session.get("user_id")
    if users.objects.filter(user_id=user_id).exists():
        user = users.objects.get(user_id=user_id)
        context["user"] = user
    else:
        return HttpResponse("error")

    with open(static_dir + '\\css\\settings\\edit-profile.css', 'r') as data:
        context['edit_profile_css'] = data.read()

    return render(request, "settings/edit_profile.html", context)

# Saves the changes done in settings to your profile
def editprofile_savechanges(request):
    if request.method == "POST":
        # Only POST requests are allowed
        form = QueryDict.dict(request.POST)

        # Get inputs
        nickname = form["nickname"]
        description = form["description"]

        # Check if nickname is empty, under 5 chars or over 30 chars
        if len(nickname) > 30 or len(nickname) < 5:
            return HttpResponse("error")

        # If description is empty, change it to "No description"
        if not description:
            description = "No description"

        # Save changes to database
        user_id = request.session.get("user_id")
        if users.objects.filter(user_id=user_id).exists():
            user = users.objects.get(user_id=user_id)
            user.nickname = nickname
            user.description = description

            user.save()
        else:
            return HttpResponse("error")

        return HttpResponse("ok")
    else:
        return render(request, 'error_pages/405.html')

# Renders a modal for uploading profilepic
def profilepic_upload(request):
    context = {}
    with open(static_dir + '\\css\\modals\\profilepic-upload.css', 'r') as data:
        context['profilepic_upload_css'] = data.read()
    return render(request, "modals/profilepic_upload.html", context)

# Renders page for cropping profile picture
def profilepic_crop(request):
    # if blob isnt in url, redirect back to settings
    blob = request.GET.get("blob", False)
    if not blob:
        return HttpResponseRedirect("/settings")
    
    # Get static files
    context = {}
    context['universal_css'] = universal_css
    context['universal_js'] = universal_js
    with open(static_dir + '\\css\\settings\\profilepic-crop.css', 'r') as data:
        context['profilepic_crop_css'] = data.read()
    with open(static_dir + '\\js\\profilepic_crop.js', 'r') as data:
        context['profilepic_crop_js'] = data.read()

    return render(request, "settings/profilepic_crop.html", context)

# Handles upload of cropped profile picture
def profilepic_cropped_upload(request):
    if request.method == "POST":
        # Convert post request to dict
        form = QueryDict.dict(request.POST)
        image_data = form["image_data"]

        # Remove header from blob and get file extension
        format, imgstr = image_data.split(';base64,')
        ext = format.split("/")[-1]

        # Create image from blob, convert from base64 to an image
        image_data = base64.b64decode(imgstr)

        # Get unix timestamp for file name
        unix_now = int(time.time())
        unix_now = str(unix_now)
        image_name = unix_now + "." + ext

        # Define path to where the image will be saved
        profile_pictures_path = os.getcwd() + "\\tictactoemult\\static\\img\\profile_pictures"
        image_path = os.path.join(profile_pictures_path, image_name)

        # Save image
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
        # Get most used color for banner color with color thief
        color_thief = ColorThief(image_path)
        dominant_color = color_thief.get_color(quality=1)

        # Convert rgb value to one that can be used by CSS
        css_rgb = "rgb" + str(dominant_color)

        # Get user info
        user_id = request.session.get("user_id")
        if users.objects.filter(user_id=user_id).exists():
            user = users.objects.get(user_id=user_id)
        else:
            return HttpResponse("error")

        # Delete old profile pic from server
        old_profilepic_path = (profile_pictures_path + "\\" + user.profile_picture)
        if os.path.exists(old_profilepic_path) and not user.profile_picture == "defaultprofile.jpg" :
            os.remove(old_profilepic_path)


        # Save new image name and banner color in database
        user.profile_picture = image_name
        user.banner_color = css_rgb
        user.save()
        
        return HttpResponse("ok")
    else :
        return render(request, 'error_pages/405.html')

# Renders a modal of a users profile
def display_profile(request, uid):
    # Get user details
    user = get_object_or_404(users, user_id=uid)
    context = {}
    context["nickname"] = user.nickname
    context["username"] = user.username
    context["banner_color"] = user.banner_color
    context["profile_picture"] = user.profile_picture
    context["description"] = user.description
    context["joindate"] = user.joindate

    # Get static files
    with open(static_dir + '\\css\\modals\\display-profile.css', 'r') as data:
        context['display_profile_css'] = data.read()

    return render(request, "modals/display_profile.html", context)

# Page in settings for changing personal information
def personal_information(request):
    context = {}
    # Get user info to display
    user_id = request.session.get("user_id")
    if users.objects.filter(user_id=user_id).exists():
        user = users.objects.get(user_id=user_id)
        context["user"] = user
    else:
        return HttpResponse("error")
    
    # Get static files
    with open(static_dir + '\\css\\settings\\personal-information.css', 'r') as data:
        context['personal_information_css'] = data.read()

    # Get forms
    context["email_form"] = PersonalInformationEmail()
    context["passwordform"] = AccountRecoveryFormNewPassword()

    return render(request, "settings/personal_information.html", context)