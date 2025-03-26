from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, QueryDict, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from .forms import LoginForm, CreateAccountForm, AccountRecoveryForm1, AccountRecoveryForm2, AccountRecoveryFormNewPassword, PersonalInformationEmail
from django.contrib.auth.hashers import make_password, check_password
from .models import users, recovery_codes, friend_list, pending_friends, match, matchmaking, leaderboard
import os
import uuid
import datetime
from pathlib import Path
import time
from datetime import datetime, timedelta
import json
from .mail import send_mail
import random
import base64
from colorthief import ColorThief
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
import string

# Create your views here.

# Sets global varible for static directory
static_dir = os.getcwd() + '\\tictactoemult\\static'
media_dir = os.getcwd() + '\\media'

# Function for loading in static js and css files
def importStaticFiles(name):
    context = {}
    # universal files
    with open(static_dir + '\\css\\universal.css', 'r') as file:
        context["universal_css"] = file.read()
    with open(static_dir + '\\js\\universal.js', 'r') as file:
        context["universal_js"] = file.read()

    # Specific files
    with open(static_dir + '\\css\\' + name + '.css', 'r') as file:
        context[f"{name}_css"] = file.read()
    with open(static_dir + '\\js\\' + name + '.js', 'r') as file:
        context[f"{name}_js"] = file.read()

    return context

# Function for rendering index/login page
def index(request):
    # The default index.html page, with a form for logging in
    context = importStaticFiles("index")

    context['form'] = LoginForm()

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
                return JsonResponse({"error" : "wrong"}, status=400)
            
            # Check that password is correct
            user = users.objects.get(username=username)
            if not check_password(password, user.password):
                return JsonResponse({"error" : "wrong"}, status=401)
            
            # set session variable
            uuid_str = str(user.user_id)
            request.session['user_id'] = uuid_str

            # If user wanted to stay logged in
            response = JsonResponse({"redirect" : 1})
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
            return JsonResponse({"error" : "error"}, status=400)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Function to render main page
def main(request):
    # If user is not logged in, redirect them
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")

    context = importStaticFiles("main")

    # Get information about user for things like profilepic, username etc
    user_id = request.session.get("user_id")
    if users.objects.filter(user_id=user_id).exists():
        user = users.objects.get(user_id=user_id)
        context["user"] = user

        # Get leaderboard stats
        leaderboard_row = leaderboard.objects.get(user_id=user_id)
        context["wins"] = leaderboard_row.wins
        context["losses"] = leaderboard_row.losses
        context["matches_played"] = leaderboard_row.matches_played

        # Calculate win loss ration
        if leaderboard_row.wins != 0 and leaderboard_row.losses != 0:
            win_loss = leaderboard_row.wins / leaderboard_row.losses
        else:
            win_loss = 0

        context["win_loss_ratio"] = win_loss
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
    context = importStaticFiles("create_account")
    context['form'] = CreateAccountForm()
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
                    return JsonResponse({"error" : "ascii"}, status=400)

            # Check if username is taken
            if users.objects.filter(username=username).exists():
                return JsonResponse({"error" : "taken"}, status=400)
            
            # Check if email is already registered
            if users.objects.filter(email=email).exists():
                return JsonResponse({"error" : "email_taken"}, status=400)
            
            # Check if username is only numbers
            if username.isdigit():
                return JsonResponse({"error" : "numeric"}, status=400)

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

            # Register user to leaderboard
            leaderboard_user = leaderboard(
                user_id = user.user_id
            )
            leaderboard_user.save()

            # Set session variables
            user = users.objects.get(username=username)
            uuid_str = str(user.user_id)
            request.session['user_id'] = uuid_str

            return JsonResponse({"redirect" : 1})
        else:
            return JsonResponse({"error" : "error"}, status=400)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Function to validate username while user is typing it in
def username_validate(request):
    if request.method == "POST":
        # Only POST requests are allowed

        # Get posted username
        data = json.loads(request.body)
        username = data.get("username")

        validate_list = {
            "ascii" : 0,
            "between_letters" : 0,
            "taken" : 0,
            "numeric" : 0
        }

        # Check if username has non english characters
        whitelist = "abcdefghijklmnopqrstuvwxyz1234567890"
        username_lower = username.lower()
        for c in username_lower:
            if c not in whitelist:
                validate_list['ascii'] = 1
        
        # Check if username is between 5 to 30 letters
        if len(username) > 30 or len(username) < 5:
            validate_list['between_letters'] = 1
        
        # Check if username is taken
        if users.objects.filter(username=username).exists():
            validate_list["taken"] = 1
        
        # Check if username is only numbers
        if username.isdigit():
            validate_list["numeric"] = 1

        return JsonResponse(validate_list)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Function that renders account recovery page
def account_recovery(request):
    context = importStaticFiles("account_recovery")
    context['form'] = AccountRecoveryForm1()

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
                return JsonResponse({"error" : "not_registered"}, status=400)

            # Generate recovery code
            recovery_code = random.randint(111111, 999999)

            # Set a expiration in unix time
            unix_now = int(time.time())
            expire = unix_now + (60 * 15) # 15 minutes

            # Send email
            mail_status = send_mail(email, "Tic Tac Toe - Recovery code", "Hi " + email + ". Your recovery code is: " + str(recovery_code))
            if mail_status == "error":
                return JsonResponse({"error" : "error"}, status=500)

            # Insert temporary recovery code inside database
            code = recovery_codes(
                email = email,
                recovery_code=recovery_code,
                expire=expire
            )

            code.save()

            # Save email in session variable
            request.session['temp_recovery_email'] = email

            return JsonResponse({"redirect" : 1})
        else:
            return JsonResponse({"error" : "error"}, status=400)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

def account_recovery_inputcode(request):
    # Check if temp_recovery_email session variable is set
    if 'temp_recovery_email' not in request.session:
        return HttpResponseRedirect("/")
    context = importStaticFiles("account_recovery")

    context['form'] = AccountRecoveryForm2()

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
                return JsonResponse({"error" : "error"}, status=400)

            # Delete expired codes
            unix_now = int(time.time())
            recovery_codes.objects.filter(expire__lt=unix_now).delete()

            # Check that recovery email session variable exists
            if 'temp_recovery_email' not in request.session:
                return JsonResponse({"error" : "error"}, status=400)

            # Check if code exists in database
            email = request.session.get('temp_recovery_email')
            if not recovery_codes.objects.filter(recovery_code=code, email=email).exists():
                return JsonResponse({"error" : "expired_notfound"}, status=401)

            # Get user id of user with that email
            user = users.objects.get(email=email)
            uuid_str = str(user.user_id)
            request.session['temp_recovery_uid'] = uuid_str

            return JsonResponse({"redirect" : 1})
        else:
            return JsonResponse({"error" : "error"}, status=400)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Function to render page for the final step of account recovery
def account_recovery_final(request):
    context = importStaticFiles("account_recovery")
    context["form"] = AccountRecoveryFormNewPassword()

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
                return JsonResponse({"error" : "no_match"}, status=400)

            # Get temporary user id
            if 'temp_recovery_uid' not in request.session:
                return JsonResponse({"error" : "error"}, status=400)
            uid = request.session.get('temp_recovery_uid')

            # Check if new password is the same as old password
            user = users.objects.get(user_id=uid)
            old_password_hash = user.password

            if check_password(new_password, old_password_hash):
                return JsonResponse({"error" : "same"}, status=400)

            # Hash new password and save it
            password_hash = make_password(new_password)

            user.password = password_hash
            user.save()

            return JsonResponse({"ok" : 1})
        else:
            return JsonResponse({"error" : "error"}, status=400)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

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
    
    context = importStaticFiles("settings")

    # Get user info to display
    user_id = request.session.get("user_id")
    user = users.objects.get(user_id=user_id)
    context["user"] = user

    return render(request, 'settings.html', context)

# renders page for editing profile in user settings
def edit_profile(request):
    context = {}

    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")

    # Get user info to display
    user_id = request.session.get("user_id")
    if users.objects.filter(user_id=user_id).exists():
        user = users.objects.get(user_id=user_id)
        context["user"] = user
    else:
        return HttpResponse("error", status=400)

    with open(static_dir + '\\css\\edit-profile.css', 'r') as data:
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

        # Check if nickname is empty
        if nickname.isspace():
            return JsonResponse({"error" : "error"}, status=400)

        # Check if nickname is under 5 chars or over 30 chars
        if len(nickname) > 30 or len(nickname) < 5:
            return JsonResponse({"error" : "error"}, status=400)

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
            return JsonResponse({"error" : "error"}, status=400)

        return JsonResponse({"ok" : 1})
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Renders a modal for uploading profilepic
def profilepic_upload(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")
    context = {}
    with open(static_dir + '\\css\\profilepic-upload.css', 'r') as data:
        context['profilepic_upload_css'] = data.read()
    return render(request, "modals/profilepic_upload.html", context)

# Saves user uploaded image temporarily
def profilepic_temp_upload(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")

    # Get posted file
    file = request.FILES["file"]
    fs = FileSystemStorage()

    # Create name from unix timestamp and get file extension
    expire = 60 * 15 # 15 minutes in seconds
    file_name = int(time.time()) + expire
    file_name = str(file_name)
    file_ext = file.name.split(".")[-1]

    # Check if file type is supported
    whitelist = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in whitelist:
        return JsonResponse({"error" : "unsupported"}, status=415)

    # Check if file size is under 3MB
    file_size_mb = int((file.size / 1024) / 1024)
    if file_size_mb > 3:
        # If file size is more than 3 mb
        return JsonResponse({"error" : "too_big"}, status=413)

    # Put new name and extenison together
    file_name = file_name + "." + file_ext

    # Save the file
    filesave = fs.save(file_name, file)
    if not filesave:
        return JsonResponse({"error" : "error"}, status=500)

    # Get url for file
    file_url = fs.url(filesave)

    # Return path to file to user
    return JsonResponse({
        "file_url" : file_url
    })

# Renders page for cropping profile picture
def profilepic_crop(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")

    # if file path isnt in url, redirect back to settings
    file_url = request.GET.get("file_url", False)
    if not file_url:
        return HttpResponseRedirect("/settings")
    
    # Get static files
    context = importStaticFiles("profilepic_crop")

    return render(request, "settings/profilepic_crop.html", context)

# Handles upload of cropped profile picture
def profilepic_cropped_upload(request):
    if request.method == "POST":
        # Delete all expired temp files
        unix_now = int(time.time())
        for filename in os.listdir(media_dir):
            f = os.path.join(media_dir, filename)
            # checking if it is a file
            if os.path.isfile(f):
                # Get expiration timestamp from filename
                timestamp = Path(f).stem
                timestamp = int(timestamp)
                if timestamp < unix_now:
                    os.remove(f)

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
            return HttpResponse("error", status=400)

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
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Renders a modal of a users profile
def display_profile(request, uid):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")

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
    with open(static_dir + '\\css\\display-profile.css', 'r') as data:
        context['display_profile_css'] = data.read()

    return render(request, "modals/display_profile.html", context)

# Page in settings for changing personal information
def personal_information(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")

    context = {}
    # Get user info to display
    user_id = request.session.get("user_id")
    if users.objects.filter(user_id=user_id).exists():
        user = users.objects.get(user_id=user_id)
        context["user"] = user
    else:
        return HttpResponse("error", status=400)
    
    # Get static files
    with open(static_dir + '\\css\\personal-information.css', 'r') as data:
        context['personal_information_css'] = data.read()

    # Get forms
    context["email_form"] = PersonalInformationEmail()
    context["passwordform"] = AccountRecoveryFormNewPassword()

    return render(request, "settings/personal_information.html", context)

# Renders modal for confirming email change in settings
def change_email_modal(request):
    if request.method == "POST":
        form = PersonalInformationEmail(request.POST)

        if form.is_valid():
            # Get posted email
            new_email = form.cleaned_data["new_email"]
            confirm_new_email = form.cleaned_data["confirm_new_email"]

            # Check if emails match
            if new_email != confirm_new_email:
                return HttpResponse("match", status=400)
            
            # Check if email is already registered
            if users.objects.filter(email=new_email).exists():
                return HttpResponse("email_taken", status=400)

            # Save email in session variable
            request.session['temp_new_email'] = new_email

            # Set contexts
            context = {}
            context["password_or_email"] = "e-mail"
            context["form"] = AccountRecoveryForm2()
            context["form_action"] = "/change_email_modal_confirm"
            context["form_id"] = "change-email-form-confirm"

            # Send e-mail with code to verify that user wants to change mail

            # Generate recovery code
            recovery_code = random.randint(111111, 999999)

            # Set a expiration in unix time
            unix_now = int(time.time())
            expire = unix_now + (60 * 15) # 15 minutes

            # Get users current email
            user_id = request.session.get("user_id")
            if users.objects.filter(user_id=user_id).exists():
                user = users.objects.get(user_id=user_id)
                context["user"] = user
            else:
                return HttpResponse("error", status=400)

            # Send email
            email = user.email
            mail_status = send_mail(email, "Tic Tac Toe - Change e-mail", "Hi " + email + ". We see that you are trying to change your e-mail. The code to change it is: <b>" + str(recovery_code) + "</b>. If this is a mistake, please contact user support at: support@jakobjohannes.com")
            if mail_status == "error":
                return HttpResponse("error", status=500)

            # Insert temporary code inside database
            code = recovery_codes(
                email = email,
                recovery_code=recovery_code,
                expire=expire
            )

            code.save()

            # Set static files
            with open(static_dir + '\\css\\change-email-password.css', 'r') as data:
                context['change_email_password_css'] = data.read()
            
            return render(request, "modals/change_email_password.html", context)
        else:
            return HttpResponse("error", status=400)
    else :
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Form handler for inputting code when code has been sent to change emails
def change_email_modal_confirm(request):
    if request.method == "POST":
        form = AccountRecoveryForm2(request.POST)

        if form.is_valid():
            # Get posted code
            code = form.cleaned_data["code"]

            # Check if code is integer
            try:
                code = int(code)
            except:
                return JsonResponse({"error" : "error"}, status=400)

            # Delete expired codes
            unix_now = int(time.time())
            recovery_codes.objects.filter(expire__lt=unix_now).delete()

            # Check that new email session variable exists
            if 'temp_new_email' not in request.session:
                return JsonResponse({"error" : "error"}, status=400)

            # Get users current email
            user_id = request.session.get("user_id")
            if users.objects.filter(user_id=user_id).exists():
                user = users.objects.get(user_id=user_id)
                email = user.email
            else:
                return JsonResponse({"error" : "error"}, status=400)

            # Check if code exists in database
            if not recovery_codes.objects.filter(recovery_code=code, email=email).exists():
                return JsonResponse({"error" : "expired_notfound"}, status=401)

            # Change email
            user.email = request.session.get("temp_new_email")
            user.save()

            # Unset session variable
            del request.session["temp_new_email"]

            return JsonResponse({"ok" : 1})
        else:
            return JsonResponse({"error" : "error"}, status=400)
    else :
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Renders modal for confirming password change in settings
def change_password_modal(request):
    if request.method == "POST":
        form = AccountRecoveryFormNewPassword(request.POST)

        if form.is_valid():
            # Get posted passwords
            new_password = form.cleaned_data["new_password"]
            confirm_new_password = form.cleaned_data["new_password_confirm"]

            # Check if passwords match
            if new_password != confirm_new_password:
                return HttpResponse("match", status=400)

            context = {}

            # Get users current email and password
            user_id = request.session.get("user_id")
            if users.objects.filter(user_id=user_id).exists():
                user = users.objects.get(user_id=user_id)
                context["user"] = user
            else:
                return HttpResponse("error", status=400)

            # Check if old password is the same as new password
            old_password_hash = user.password
            if check_password(new_password, old_password_hash):
                return HttpResponse("same", status=400)

            new_password_hash = make_password(new_password)

            # Save password hash in session variable
            request.session['temp_new_password'] = new_password_hash

            # Set contexts
            context["password_or_email"] = "password"
            context["form"] = AccountRecoveryForm2()
            context["form_action"] = "/change_password_modal_confirm"
            context["form_id"] = "change-password-form-confirm"

            # Send e-mail with code to verify that user wants to change password

            # Generate recovery code
            recovery_code = random.randint(111111, 999999)

            # Set a expiration in unix time
            unix_now = int(time.time())
            expire = unix_now + (60 * 15) # 15 minutes

            # Send email
            email = user.email
            mail_status = send_mail(email, "Tic Tac Toe - Change password", "Hi " + email + ". We see that you are trying to change your password. The code to change it is: <b>" + str(recovery_code) + "</b>. If this is a mistake, please contact user support at: support@jakobjohannes.com")
            if mail_status == "error":
                return HttpResponse("error", status=500)

            # Insert temporary code inside database
            code = recovery_codes(
                email = email,
                recovery_code=recovery_code,
                expire=expire
            )

            code.save()

            # Set static files
            with open(static_dir + '\\css\\change-email-password.css', 'r') as data:
                context['change_email_password_css'] = data.read()
            
            return render(request, "modals/change_email_password.html", context)
        else:
            return HttpResponse("error", status=400)
    else :
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Form handler for inputting code when code has been sent to change password
def change_password_modal_confirm(request):
    if request.method == "POST":
        form = AccountRecoveryForm2(request.POST)

        if form.is_valid():
            # Get posted code
            code = form.cleaned_data["code"]

            # Check if code is integer
            try:
                code = int(code)
            except:
                return JsonResponse({"error" : "error"}, status=400)

            # Delete expired codes
            unix_now = int(time.time())
            recovery_codes.objects.filter(expire__lt=unix_now).delete()

            # Check that new email session variable exists
            if 'temp_new_password' not in request.session:
                return JsonResponse({"error" : "error"}, status=400)

            # Get users current email
            user_id = request.session.get("user_id")
            if users.objects.filter(user_id=user_id).exists():
                user = users.objects.get(user_id=user_id)
                email = user.email
            else:
                return JsonResponse({"error" : "error"}, status=400)

            # Check if code exists in database
            if not recovery_codes.objects.filter(recovery_code=code, email=email).exists():
                return JsonResponse({"error" : "expired_notfound"}, status=401)

            # Change password
            user.password = request.session.get("temp_new_password")
            user.save()

            # Unset session variable
            del request.session["temp_new_password"]

            return JsonResponse({"ok" : 1})
        else:
            return JsonResponse({"error" : "error"}, status=400)
    else :
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Renders template for friends page
def friends(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")

    # Set static files
    context = importStaticFiles("friends")

    return render(request, "friends.html", context)

# Renders your friends tab in friends page
def your_friends(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")
    else:
        user_id = request.session.get("user_id")

    # Make 2 arrays. One containg online friends and one containing offline friends
    online_friends = []
    offline_friends = []

    # Get current unix timestamp
    unix_now = int(time.time())

    # Get users friend list
    friends = friend_list.objects.filter(user_id_1=user_id)
    for friend in friends:
        # Get info about each friend
        friend_user_id = friend.user_id_2
        friend = users.objects.get(user_id=friend_user_id)

        # If friend is online, add to online array. If not, add to offline array
        if friend.ping > unix_now:
            online_friends.append(friend)
        else:
            offline_friends.append(friend)
    
    # Put arrays in context
    context = {}
    context["online_friends"] = online_friends
    context["offline_friends"] = offline_friends

    # Set static files
    with open(static_dir + '\\css\\your_friends.css', 'r') as data:
        context['your_friends_css'] = data.read()
    
    return render(request, "friends/your_friends.html", context)

# Updates the ping column in users table every 5 seconds to verify that user is online
def ping(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")
    else:
        user_id = request.session.get("user_id")

    # Get current unix timestamp
    unix_now = int(time.time())

    # Make unix timestamp 10 seconds from now
    ping = unix_now + 10

    # Get user and update column
    user = users.objects.get(user_id=user_id)
    user.ping = ping
    user.save()

    return HttpResponse("pinged")

# Renders page for adding friends
def add_friends(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")
    else:
        user_id = request.session.get("user_id")
        user = users.objects.get(user_id=user_id)
        context = {}
        context["user"] = user
    
    # Set static files
    with open(static_dir + '\\css\\add_friends.css', 'r') as data:
        context['add_friends_css'] = data.read()

    return render(request, "friends/add_friends.html", context)

# Renders page for pending invites
def pending_invites(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")
    else:
        user_id = request.session.get("user_id")
        user = users.objects.get(user_id=user_id)
        context = {}
        context["user"] = user
    
    # Get all incoming pending invites
    incoming = []
    incoming_invites = pending_friends.objects.filter(incoming=user_id)
    for row in incoming_invites:
        # Get info about the friend request
        incoming_item = {}
        incoming_item["sent"] = row.sent
        incoming_item["row_id"] = row.id

        # Get info about user
        outgoing_userid = row.outgoing
        outgoing_user = users.objects.get(user_id=outgoing_userid)
        incoming_item["user_id"] = outgoing_user.user_id
        incoming_item["nickname"] = outgoing_user.nickname
        incoming_item["profile_picture"] = outgoing_user.profile_picture

        incoming.append(incoming_item)
    
    context["incoming"] = incoming

    # Get all outgoing pending invites
    outgoing = []
    outgoing_invites = pending_friends.objects.filter(outgoing=user_id)
    for row in outgoing_invites:
        # Get info about the friend request
        outgoing_item = {}
        outgoing_item["sent"] = row.sent
        outgoing_item["row_id"] = row.id

        # Get info about user
        incoming_userid = row.incoming
        incoming_user = users.objects.get(user_id=incoming_userid)
        outgoing_item["user_id"] = incoming_user.user_id
        outgoing_item["nickname"] = incoming_user.nickname
        outgoing_item["profile_picture"] = incoming_user.profile_picture

        outgoing.append(outgoing_item)

    context["outgoing"] = outgoing


    # Set static files
    with open(static_dir + '\\css\\pending_invites.css', 'r') as data:
        context['pending_invites_css'] = data.read()

    # Render template
    return render(request, "friends/pending_invites.html", context)

# Gets all the users pending invites and returns an amount of them
def pending_friends_notif(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")
    else:
        user_id = request.session.get("user_id")

    # Get the sum of all rows pending friends
    count = pending_friends.objects.filter(incoming=user_id).count()
    return JsonResponse({"amount":count})


# Renders a list of users that match search query for username and nickname
def add_friends_result(request):
    if request.method == "POST":
        # If user is not logged in, redirect
        if "user_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            user_id = request.session.get("user_id")

        # Get search query
        data = json.loads(request.body)
        query = data.get("query")

        # Get users from database where their nickname or username contains the query, limit to 10 rows
        query_users = users.objects.filter(
            Q(username__icontains=query) | Q(nickname__icontains=query)
        )[:10]

        result_users = []

        # Exclude any users in your friend list, users you have sent a request to, yourself and users that have already sent you a friend request
        for user in query_users:
            friend_uid = user.user_id
            if str(friend_uid) == user_id:
                continue
            elif friend_list.objects.filter(user_id_1=user_id, user_id_2=friend_uid).exists():
                continue
            elif pending_friends.objects.filter(outgoing=user_id, incoming=friend_uid).exists():
                continue
            elif pending_friends.objects.filter(outgoing=friend_uid, incoming=user_id).exists():
                continue
            else:
                result_users.append(user)

        # Pass into context
        context = {}
        context["users"] = result_users
        context["query"] = query

        return render(request, "friends/add_friends_result.html", context)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Sends a friend request
def send_friend_request(request):
    if request.method == "POST":
        # If user is not logged in, redirect
        if "user_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            user_id = request.session.get("user_id")

        # Get post data from json
        body = json.loads(request.body)
        friend_user_id = body["user_id"]

        # Check if user exists
        try:
            friend_user_id_uuid = uuid.UUID(friend_user_id)
            if not users.objects.filter(user_id=friend_user_id_uuid).exists():
                return JsonResponse({"error" : "noexist"}, status=400)
        except:
            return JsonResponse({"error" : "noexist"}, status=400)

        # Check if user is already in friend list
        if friend_list.objects.filter(user_id_1=user_id, user_id_2=friend_user_id).exists():
            return JsonResponse({"error" : "already_friends"}, status=400)
        
        # Check if user has already sent a friend request to this user
        if pending_friends.objects.filter(outgoing=user_id, incoming=friend_user_id).exists():
            return JsonResponse({"error" : "alreadysent"}, status=400)
        
        # Check if user has already received a friend request from this user
        if pending_friends.objects.filter(outgoing=friend_user_id, incoming=user_id).exists():
            return JsonResponse({"error" : "alreadyreceived"}, status=400)
        
        # Check if user is yourself
        if user_id == friend_user_id:
            return JsonResponse({"error" : "yourself"}, status=400)
        
        # Get current date and time for sent timestamp
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M")

        # Put friend request in pending_friends table
        pending = pending_friends(
            outgoing=user_id,
            incoming=friend_user_id,
            sent=timestamp
        )

        pending.save()

        # Send id of button to disable
        alreadysentbutton = "friendrow_sendbutton_" + friend_user_id

        return JsonResponse({
            "ok" : 1,
            "sentbutton" : alreadysentbutton
        })
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Function that deletes a row from pending_friends table
def cancel_decline_friend_request(request):
    if request.method == "POST":
        # If user is not logged in, redirect
        if "user_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            user_id = request.session.get("user_id")
        
        # Get posted row id
        body = json.loads(request.body)
        row_id = body["row_id"]

        # Check if the friend request belongs to user
        if not pending_friends.objects.filter(id=row_id, outgoing=user_id).exists() | pending_friends.objects.filter(id=row_id, incoming=user_id).exists():
            return JsonResponse({"error" : "error"}, status=400)
        
        # Delete the row
        row = pending_friends.objects.get(id=row_id)
        row.delete()

        return JsonResponse({"ok" : 1})
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Function that inserts rows for friend list in friends_list table
def accept_friend_request(request):
    if request.method == "POST":
        # If user is not logged in, redirect
        if "user_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            user_id = request.session.get("user_id")
        
        # Get post data
        body = json.loads(request.body)
        row_id = body["row_id"]

        # Check if the pending_friend row exists, and if your user id is in the incoming column
        if not pending_friends.objects.filter(id=row_id, incoming=user_id).exists():
            return JsonResponse({"error" : "error"}, status=400)
        else:
            row = pending_friends.objects.get(id=row_id)
        
        # Get other user id for friend list table
        user_id_2 = row.outgoing

        # Delete pending friend request
        row.delete()

        # Get current date for when users became friends
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M")

        # Insert rows into friend list table
        row = friend_list(
            user_id_1=user_id,
            user_id_2=user_id_2,
            became_friends=timestamp
        )

        row.save()

        row = friend_list(
            user_id_1=user_id_2,
            user_id_2=user_id,
            became_friends=timestamp
        )

        row.save()

        return JsonResponse({"ok" : 1})
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Function that gives a list of online friends
def main_online_friends(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")
    else:
        user_id = request.session.get("user_id")

    # Get all friends
    context = {}
    online_friends = []
    friends = friend_list.objects.filter(user_id_1=user_id)
    for user in friends:
        friend_uid = user.user_id_2
        friend = users.objects.get(user_id=friend_uid)
        unix_now = int(time.time())
        # If friend is online, append to list of online friends
        if friend.ping > unix_now:
            online_friends.append(friend)

    context["online_friends"] = online_friends

    return render(request, "main_online_friends.html", context)

# Renders modal for managing friend
def manage_friend(request):
    if request.method == "POST":
        # If user is not logged in, redirect
        if "user_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            user_id = request.session.get("user_id")
        
        # Get posted user id
        body = json.loads(request.body)
        friend = body["user_id"]
        
        # Check if person is in friend list
        if not friend_list.objects.filter(user_id_1=user_id, user_id_2=friend).exists():
            return HttpResponse("error", status=400)
        
        # Get info about friend
        user = users.objects.get(user_id=friend)
        context = {}
        context["friend"] = user

        # Load static css file
        with open(static_dir + '\\css\\manage_friend.css', 'r') as data:
            context['manage_friend_css'] = data.read()

        # Render the modal
        return render(request, "friends/manage_friend.html", context)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Removes a friend from friends list
def remove_friend(request):
    if request.method == "POST":
        # If user is not logged in, redirect
        if "user_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            user_id = request.session.get("user_id")
        
        # Get posted user id
        body = json.loads(request.body)
        friend = body["user_id"]
        
        # Check if person is in friend list
        if not friend_list.objects.filter(user_id_1=user_id, user_id_2=friend).exists():
            return JsonResponse({"error" : "not_friend"}, status=400)
        
        # Remove friend from friend list
        friend_list.objects.filter(user_id_1=user_id, user_id_2=friend).delete()

        # Remove yourself from friends friend list
        friend_list.objects.filter(user_id_1=friend, user_id_2=user_id).delete()

        # Everything went well, return ok
        return JsonResponse({"ok":1}, status=200)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Renders matchmaking page
def matchmaking_page(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")
    else:
        user_id = request.session.get("user_id")
    
    # If animation from previous match was done, reset it
    if "animation_sequence" in request.session:
        del request.session["animation_sequence"]

    # Set static files
    context = importStaticFiles("matchmaking")
    context["user_id"] = user_id

    return render(request, "matchmaking.html", context)

# Backend that gets ran on load of matchmaking page
def matchmaking_onload(request):
    if request.method == "POST":
        # Get post data
        body = json.loads(request.body)
        user_id = body["user_id"]
        gamemode = body["gamemode"]

        # Define null in uuid form
        uuid_null = "00000000000000000000000000000000"

        if gamemode == "r":
            # Gamemode is random
            
            # Check matchmaking table to see if any rows dont have user id 2 filled out
            if matchmaking.objects.filter(user_id_2=uuid_null).exists():
                # Found available row
                row = matchmaking.objects.filter(user_id_2=uuid_null).first()

                # Insert user id into row
                row.user_id_2 = user_id
                row.save()

                # Save row in session var
                row_id = row.pk
                request.session['matchmaking_row_id'] = row_id

                # Return websocket message
                uuid_str = str(row.user_id_1)
                return JsonResponse({"nonefound": 0, "row_id": row_id, "user_id_1": uuid_str}, status=200)
            else:
                # Found no rows, so create one
                row = matchmaking(user_id_1 = user_id, user_id_2 = uuid_null)
                row.save()
                row_id = (matchmaking.objects.last()).pk

                # Save row in session var
                request.session['matchmaking_row_id'] = row_id
                
                # Pass none found message into context
                return JsonResponse({"nonefound": 1, "id": row_id}, status=200)
        elif gamemode == "f":
            # Gamemode is invite friend
            print("dkldk")
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Cancels matchmaking
def matchmaking_cancel(request):
    if request.method == "GET":
        # Get row id in session
        if "matchmaking_row_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            row_id = request.session.get("matchmaking_row_id")

        # Delete row from matchmaking table
        matchmaking.objects.get(pk=row_id).delete()

        # Return response
        return JsonResponse({"ok": 1, "row_id": row_id}, status=200)
    else:
        allowed = ['GET']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

def check_joined_row(request):
    if request.method == "POST":
        # Get row id in session
        if "matchmaking_row_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            matchmaking_row_id = request.session.get("matchmaking_row_id")

        # If user is not logged in, redirect
        if "user_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            user_id = request.session.get("user_id")

        # Check if the row and user_id matches the row youre in
        body = json.loads(request.body)
        user_id_1 = body["user_id_1"]
        row_id = body["row_id"]

        if user_id_1 == user_id:
            if matchmaking.objects.filter(user_id_1=user_id, pk=row_id).exists():
                # The row is your row, create a random room name
                length = 16
                room_name = ''.join(random.choices(string.ascii_letters + string.digits, k=length))

                # Get info from matchmaking row
                matchmaking_row = matchmaking.objects.get(pk=matchmaking_row_id)
                user_id_2 = matchmaking_row.user_id_2

                # Create random turn
                random_turn = random.randint(1,2)
                if random_turn == 1:
                    turn = user_id_1
                else:
                    turn = user_id_2
                
                # Figure out who is x and o
                random_xo = random.randint(1,2)
                if random_xo == 1:
                    x = user_id_1
                    o = user_id_2
                else:
                    x = user_id_2
                    o = user_id_1
                
                # Define timer. Each turn lasts a minute
                unix_now = int(time.time())
                timer = unix_now + 60

                # Define ping
                unix_ping = unix_now + 10
                
                # Define taken slots
                taken_slots = json.dumps({
                    1: 0,
                    2: 0,
                    3: 0,
                    4: 0,
                    5: 0,
                    6: 0,
                    7: 0,
                    8: 0,
                    9: 0
                })

                # Create a new row in the match table
                row = match(
                    user_id_1 = user_id,
                    user_id_2 = user_id_2,
                    turn = turn,
                    taken_slots = taken_slots,
                    room_name = room_name,
                    timer = timer,
                    x = x,
                    o = o,
                    user_id_1_ping = unix_ping,
                    user_id_2_ping = unix_ping
                )
                row.save()

                # Add match played in leaderboard
                user_id_1_leaderboard = leaderboard.objects.get(user_id=user_id_1)
                user_id_2_leaderboard = leaderboard.objects.get(user_id=user_id_2)

                user_id_1_leaderboard.matches_played = user_id_1_leaderboard.matches_played + 1
                user_id_1_leaderboard.save()

                user_id_2_leaderboard.matches_played = user_id_2_leaderboard.matches_played + 1
                user_id_2_leaderboard.save()

                # Delete session var from matchmaking
                del request.session["matchmaking_row_id"]

                # Return response
                return JsonResponse({
                    "yourrow": 1,
                    "user_id": user_id_2,
                    "row_id": matchmaking_row_id,
                    "room_name": room_name
                })
            else:
                return JsonResponse({"yourrow": 0}, status=200)
        else:
            return JsonResponse({"yourrow": 0}, status=200)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Check if a match that was created includes you
def check_match_created(request):
    if request.method == "POST":
        # Get row id in session
        if "matchmaking_row_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            matchmaking_row_id = request.session.get("matchmaking_row_id")

        # If user is not logged in, redirect
        if "user_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            user_id = request.session.get("user_id")

        # Check if the your user id is in the room
        body = json.loads(request.body)
        user_id_fetch = body["user_id"]
        room_name = body["room_name"]

        if user_id_fetch == user_id:
            if match.objects.filter(user_id_2=user_id, room_name=room_name).exists():
                # Match has you in it, delete matchmaking row and remove session vars from matchmaking
                matchmaking.objects.get(pk=matchmaking_row_id).delete()
                del request.session["matchmaking_row_id"]

                # Send message to redirect to room
                return JsonResponse({"yourmatch": 1}, status=200)
            else:
                return JsonResponse({"yourmatch": 0}, status=200)
        else:
            return JsonResponse({"yourmatch": 0}, status=200)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

def match_page(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")
    else:
        user_id = request.session.get("user_id")
    context = importStaticFiles("match")
    context["user_id"] = user_id
    return render(request, "match.html", context)

# Gives info for animation sequence
def match_animation_sequence(request):
    if request.method == "POST":
        # If user is not logged in, redirect
        if "user_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            user_id = request.session.get("user_id")
        
        # Check if animation has already been done
        if "animation_sequence" not in request.session or request.session.get("animation_sequence") == 0:
            # Get the room name
            body = json.loads(request.body)
            room_name = body["room_name"]

            # check if room exists
            if match.objects.filter(room_name=room_name).exists():
                match_row = match.objects.get(room_name=room_name)

                # Check if user is in the match
                if str(match_row.user_id_1) == user_id or str(match_row.user_id_2) == user_id:
                    # Get profilepic and nickname of users
                    user_id_1 = match_row.user_id_1
                    user_id_2 = match_row.user_id_2

                    user_id_1_row = users.objects.get(user_id=user_id_1)
                    user_id_2_row = users.objects.get(user_id=user_id_2)

                    # Get x user id
                    x = match_row.x

                    # Set session variable to be 1
                    request.session['animation_sequence'] = 1

                    return JsonResponse({
                        "user_id_1": user_id_1,
                        "user_id_2": user_id_2,
                        "user_id_1_nickname": user_id_1_row.nickname,
                        "user_id_2_nickname": user_id_2_row.nickname,
                        "user_id_1_profilepic": user_id_1_row.profile_picture,
                        "user_id_2_profilepic": user_id_2_row.profile_picture,
                        "x": x,
                        "done": 0
                    }, status=200)
                else:
                    return JsonResponse({"error": "noaccess"}, status=403)
            else:
                return JsonResponse({"error": "notfound"}, status=404)
        else:
            return JsonResponse({"done": 1}, status=200)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Gets various info of the match the current user is in
def get_match_info(request, room_name, user_round):
    if request.method == "GET":
        # If user is not logged in, redirect
        if "user_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            user_id = request.session.get("user_id")
        
        # Check if user is allowed in match
        if match.objects.filter(room_name=room_name).exists():
            match_row = match.objects.get(room_name=room_name)
            if str(match_row.user_id_1) == user_id or str(match_row.user_id_2) == user_id:
                # User is in match
                final_win = "none"
                
                # Get slots
                match_slots = match_row.taken_slots

                # Get nickname and profile pic of x and o
                x_uid = match_row.x
                o_uid = match_row.o

                x_row = users.objects.get(user_id=x_uid)
                x_nickname = x_row.nickname
                x_profilepic = x_row.profile_picture

                o_row = users.objects.get(user_id=o_uid)
                o_nickname = o_row.nickname
                o_profilepic = o_row.profile_picture

                # Get time left from match timer start
                unix_now = int(time.time())
                seconds = match_row.timer - unix_now

                # If time ran out, change turns
                if (seconds <= 0):
                    # Update the turn
                    if match_row.turn == match_row.user_id_1:
                        turn = match_row.user_id_2
                    elif match_row.turn == match_row.user_id_2:
                        turn = match_row.user_id_1
                    
                    # Update timer
                    unix_now = int(time.time())
                    timer = unix_now + 60

                    # Update row in database
                    match_row.turn = turn
                    match_row.timer = timer
                    match_row.save()

                # Get whos turn it is
                if match_row.turn == x_uid:
                    turn = "x"
                else:
                    turn = "o"
                
                # Get the current round
                round = match_row.round

                # Define winning patterns
                match_slots_dict = json.loads(match_row.taken_slots)
                winning_patterns = [
                    [1, 2, 3],
                    [1, 4, 7],
                    [1, 5, 9],
                    [2, 5, 8],
                    [3, 6, 9],
                    [3, 5, 7],
                    [4, 5, 6],
                    [7, 8, 9]
                ]

                # Define slots that x has
                x_slots = []
                for key in match_slots_dict:
                    if match_slots_dict[key] == "x":
                        x_slots.append(int(key))
                
                # Define slots that o has
                o_slots = []
                for key in match_slots_dict:
                    if match_slots_dict[key] == "o":
                        o_slots.append(int(key))

                # See if they have winning patterns
                match_outcome = "none"
                for pattern in winning_patterns:
                    x_count = 0
                    o_count = 0
                    for element in pattern:
                        if int(element) in x_slots:
                            x_count += 1
                        if int(element) in o_slots:
                            o_count += 1
                    if x_count == 3:
                        match_outcome = "x"
                        break
                    elif o_count == 3:
                        match_outcome = "o"
                        break

                # See if match is a draw
                if match_outcome == "none":
                    tie = 0
                    for key in match_slots_dict:
                        if match_slots_dict[key] != 0:
                            tie += 1
                    
                    if tie >= 9:
                        match_outcome = "tie"
                    else:
                        match_outcome = "none"
                
                # See if its a win or tie
                if match_outcome != "none":
                    match_status_temp = str(match_row.match_status )
                    match_status_dict = json.loads(match_status_temp)
                    if match_outcome == "x":
                        # x won
                        message = f"{x_nickname} won."
                        match_status_dict[round] = {"result": "win", "won": "x", "message": message}
                    elif match_outcome == "o":
                        # o won
                        message = f"{o_nickname} won."
                        match_status_dict[round] = {"result": "win", "won": "o", "message": message}
                    elif match_outcome == "tie":
                        # It was a tie
                        message = "It was a tie"
                        match_status_dict[round] = {"result": "tie", "message": message}

                    # Reset match slots
                    taken_slots = json.dumps({
                        1: 0,
                        2: 0,
                        3: 0,
                        4: 0,
                        5: 0,
                        6: 0,
                        7: 0,
                        8: 0,
                        9: 0
                    })

                    # Increment round
                    round = round + 1
                    newround = 1

                    # Update the match status
                    match_status = json.dumps(match_status_dict)

                    # Update the row
                    match_row.taken_slots = taken_slots
                    match_row.round = round
                    match_row.match_status = match_status
                    match_row.save()
                else:
                    newround = 0

                # Check if user needs match status
                if user_round < round:
                    match_status_dict = json.loads(match_row.match_status)
                    match_status_response = json.dumps(match_status_dict[str(user_round)])
                else:
                    match_status_response = "none"

                # Refresh the taken slots
                match_slots = match_row.taken_slots

                # Check if anyone left
                if str(match_row.left) != "00000000-0000-0000-0000-000000000000":
                    left_uid = match_row.left

                    # Update table to give win to person who didnt leave and delete row
                    if str(left_uid) != user_id:
                        final_win = json.dumps({"uid": user_id, "reason": "Opponent left the match."})

                        # Update leaderboard
                        user_id_leaderboard = leaderboard.objects.get(user_id=user_id)
                        user_id_leaderboard.wins = user_id_leaderboard.wins + 1
                        user_id_leaderboard.save()

                        # Delete the row
                        match.objects.get(pk=match_row.pk).delete()

                # Return response
                return JsonResponse({
                    "allowed": 1,
                    "slots": match_slots,
                    "x_nickname": x_nickname,
                    "o_nickname": o_nickname,
                    "x_profilepic": x_profilepic,
                    "o_profilepic": o_profilepic,
                    "turn": turn,
                    "seconds": seconds,
                    "x_uid": x_uid,
                    "o_uid": o_uid,
                    "round": round,
                    "match_status": match_status_response,
                    "newround": newround,
                    "final_win": final_win
                }, status=200)
            else:
                # Kick user because theyre not in match
                return JsonResponse({"allowed": 0}, status=403)
        else:
            # Kick user because match doesnt exist.
            return JsonResponse({"allowed": 0}, status=404)
    else:
        allowed = ['GET']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Verifies a move in match and updates database
def match_do_move(request):
    if request.method == "POST":
        # If user is not logged in, redirect
        if "user_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            user_id = request.session.get("user_id")

        # Get JSON data
        body = json.loads(request.body)
        room_name = body["room_name"]
        slot_id = body["slot_id"]

        # Check if match exists
        if match.objects.filter(room_name=room_name).exists():
            match_row = match.objects.get(room_name=room_name)
            if str(match_row.user_id_1) == user_id or str(match_row.user_id_2) == user_id:
                # User is in match, check if its their turn
                if str(match_row.turn) == user_id:
                    # It is users turn, check if slot is taken
                    slots = json.loads(match_row.taken_slots)
                    if slots[slot_id] == 0:
                        # Slot is not taken

                        # Check if user is x or o
                        if str(match_row.x) == user_id:
                            slot_value = "x"
                        else:
                            slot_value = "o"

                        # Update the slot
                        slots[slot_id] = slot_value
                        slots = json.dumps(slots)

                        # Update the turn
                        if str(match_row.user_id_1) == user_id:
                            turn = match_row.user_id_2
                        else:
                            turn = match_row.user_id_1
                        
                        # Update timer
                        unix_now = int(time.time())
                        timer = unix_now + 60

                        # Update row in database
                        match_row.taken_slots = slots
                        match_row.turn = turn
                        match_row.timer = timer
                        match_row.save()

                        return JsonResponse({"allowed": 1,"available": 1, "turn":1}, status=200)
                    else:
                        # Slot is already taken
                        return JsonResponse({"allowed": 1,"available": 0, "turn":1}, status=200)
                else:
                    # It is not the users turn
                    return JsonResponse({"allowed": 1,"turn": 0, "available": 0}, status=200)
            else:
                # Kick user because theyre not in match
                return JsonResponse({"allowed": 0}, status=403)
        else:
            # Kick user because match doesnt exist.
            return JsonResponse({"allowed": 0}, status=404)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Renders a modal for confirming leaving match
def leave_match_modal(request):
    # If user is not logged in, redirect
    if "user_id" not in request.session:
        return HttpResponseRedirect("/")

    # Get css file
    context = {}
    with open(static_dir + '\\css\\leave-match-modal.css', 'r') as data:
        context['leave_match_modal_css'] = data.read()

    return render(request, "modals/leave_match_modal.html", context)

# Leaves the current match youre in
def leave_match(request):
    if request.method == "POST":
        # If user is not logged in, redirect
        if "user_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            user_id = request.session.get("user_id")

        # Get JSON data
        body = json.loads(request.body)
        room_name = body["room_name"]

        # Check if match exists
        if match.objects.filter(room_name=room_name).exists():
            match_row = match.objects.get(room_name=room_name)
            if str(match_row.user_id_1) == user_id or str(match_row.user_id_2) == user_id:
                # User is in match, change left row
                match_row.left = user_id
                match_row.save()

                # Update leaderboard
                leaderboard_row = leaderboard.objects.get(user_id=user_id)
                leaderboard_row.losses = leaderboard_row.losses + 1
                leaderboard_row.save()

                # Return
                return JsonResponse({"ok" : 1})
            else:
                # Kick user because theyre not in match
                return JsonResponse({"allowed": 0}, status=403)
        else:
            # Kick user because match doesnt exist.
            return JsonResponse({"allowed": 0}, status=404)
    else:
        allowed = ['POST']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")

# Long polling for unix timestamp of users in match
def match_ping(request, room_name):
    if request.method == "GET":
        # If user is not logged in, redirect
        if "user_id" not in request.session:
            return HttpResponseRedirect("/")
        else:
            user_id = request.session.get("user_id")

        # Check if match exists
        if match.objects.filter(room_name=room_name).exists():
            match_row = match.objects.get(room_name=room_name)
            if str(match_row.user_id_1) == user_id or str(match_row.user_id_2) == user_id:
                # User is in match

                # Get current unix timestamp
                unix_now = int(time.time())

                # Make unix timestamp 10 seconds from now
                ping_unix = unix_now + 10

                # Create ping
                if str(match_row.user_id_1) == user_id:
                    match_row.user_id_1_ping = ping_unix
                    opponent_ping = match_row.user_id_2_ping
                else:
                    match_row.user_id_2_ping = ping_unix
                    opponent_ping = match_row.user_id_1_ping

                match_row.save()

                # Check if opponent is offline
                if opponent_ping < unix_now:
                    opponent_offline = 1
                else:
                    opponent_offline = 0

                # Return
                return JsonResponse({"ok" : 1, "opponent_offline": opponent_offline})
            else:
                # Kick user because theyre not in match
                return JsonResponse({"allowed": 0}, status=403)
        else:
            # Kick user because match doesnt exist.
            return JsonResponse({"allowed": 0}, status=404)
    else:
        allowed = ['GET']
        return HttpResponseNotAllowed(allowed, f"Method not Allowed. <br> Allowed: {allowed}. <br> <a href='/'>To Login</a>")