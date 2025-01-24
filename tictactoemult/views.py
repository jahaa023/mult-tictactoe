from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, QueryDict, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from .forms import LoginForm, CreateAccountForm, AccountRecoveryForm1, AccountRecoveryForm2, AccountRecoveryFormNewPassword, PersonalInformationEmail
from django.contrib.auth.hashers import make_password, check_password
from .models import users, recovery_codes, friend_list, pending_friends
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
                return JsonResponse({"error" : "wrong"})
            
            # Check that password is correct
            user = users.objects.get(username=username)
            if not check_password(password, user.password):
                return JsonResponse({"error" : "wrong"})
            
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
            return JsonResponse({"error" : "error"})
    else:
        return HttpResponseNotAllowed("Method not allowed")

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
                    return JsonResponse({"error" : "ascii"})

            # Check if username is taken
            if users.objects.filter(username=username).exists():
                return JsonResponse({"error" : "taken"})
            
            # Check if email is already registered
            if users.objects.filter(email=email).exists():
                return JsonResponse({"error" : "email_taken"})
            
            # Check if username is only numbers
            if username.isdigit():
                return JsonResponse({"error" : "numeric"})

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

            return JsonResponse({"redirect" : 1})
        else:
            return JsonResponse({"error" : "error"})
    else:
        return HttpResponseNotAllowed("Method not allowed")

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
        return HttpResponseNotAllowed("Method not allowed")

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
                return JsonResponse({"error" : "not_registered"})

            # Generate recovery code
            recovery_code = random.randint(111111, 999999)

            # Set a expiration in unix time
            unix_now = int(time.time())
            expire = unix_now + (60 * 15) # 15 minutes

            # Send email
            mail_status = send_mail(email, "Tic Tac Toe - Recovery code", "Hi " + email + ". Your recovery code is: " + str(recovery_code))
            if mail_status == "error":
                return JsonResponse({"error" : "error"})

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
            return JsonResponse({"error" : "error"})
    else:
        return HttpResponseNotAllowed("Method not allowed")

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
                return JsonResponse({"error" : "error"})

            # Delete expired codes
            unix_now = int(time.time())
            recovery_codes.objects.filter(expire__lt=unix_now).delete()

            # Check that recovery email session variable exists
            if 'temp_recovery_email' not in request.session:
                return JsonResponse({"error" : "error"})

            # Check if code exists in database
            email = request.session.get('temp_recovery_email')
            if not recovery_codes.objects.filter(recovery_code=code, email=email).exists():
                return JsonResponse({"error" : "expired_notfound"})

            # Get user id of user with that email
            user = users.objects.get(email=email)
            uuid_str = str(user.user_id)
            request.session['temp_recovery_uid'] = uuid_str

            return JsonResponse({"redirect" : 1})
        else:
            return JsonResponse({"error" : "error"})
    else:
        return HttpResponseNotAllowed("Method not allowed")

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
                return JsonResponse({"error" : "no_match"})

            # Get temporary user id
            if 'temp_recovery_uid' not in request.session:
                return JsonResponse({"error" : "error"})
            uid = request.session.get('temp_recovery_uid')

            # Check if new password is the same as old password
            user = users.objects.get(user_id=uid)
            old_password_hash = user.password

            if check_password(new_password, old_password_hash):
                return JsonResponse({"error" : "same"})

            # Hash new password and save it
            password_hash = make_password(new_password)

            user.password = password_hash
            user.save()

            return JsonResponse({"ok" : 1})
        else:
            return JsonResponse({"error" : "error"})
    else:
        return HttpResponseNotAllowed("Method not allowed")

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
        return HttpResponse("error")

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
            return JsonResponse({"error" : "error"})

        # Check if nickname is under 5 chars or over 30 chars
        if len(nickname) > 30 or len(nickname) < 5:
            return JsonResponse({"error" : "error"})

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
            return JsonResponse({"error" : "error"})

        return JsonResponse({"ok" : 1})
    else:
        return HttpResponseNotAllowed("Method not allowed")

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
        return JsonResponse({"error" : "unsupported"})

    # Check if file size is under 3MB
    file_size_mb = int((file.size / 1024) / 1024)
    if file_size_mb > 3:
        # If file size is more than 3 mb
        return JsonResponse({"error" : "too_big"})

    # Put new name and extenison together
    file_name = file_name + "." + file_ext

    # Save the file
    filesave = fs.save(file_name, file)
    if not filesave:
        return JsonResponse({"error" : "error"})

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
        return HttpResponseNotAllowed("Method not allowed")

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
        return HttpResponse("error")
    
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
                return HttpResponse("match")
            
            # Check if email is already registered
            if users.objects.filter(email=new_email).exists():
                return HttpResponse("email_taken")

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
                return HttpResponse("error")

            # Send email
            email = user.email
            mail_status = send_mail(email, "Tic Tac Toe - Change e-mail", "Hi " + email + ". We see that you are trying to change your e-mail. The code to change it is: <b>" + str(recovery_code) + "</b>. If this is a mistake, please contact user support at: support@jakobjohannes.com")
            if mail_status == "error":
                return HttpResponse("error")

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
            return HttpResponse("error")
    else :
        return HttpResponseNotAllowed("Method not allowed")

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
                return JsonResponse({"error" : "error"})

            # Delete expired codes
            unix_now = int(time.time())
            recovery_codes.objects.filter(expire__lt=unix_now).delete()

            # Check that new email session variable exists
            if 'temp_new_email' not in request.session:
                return JsonResponse({"error" : "error"})

            # Get users current email
            user_id = request.session.get("user_id")
            if users.objects.filter(user_id=user_id).exists():
                user = users.objects.get(user_id=user_id)
                email = user.email
            else:
                return JsonResponse({"error" : "error"})

            # Check if code exists in database
            if not recovery_codes.objects.filter(recovery_code=code, email=email).exists():
                return JsonResponse({"error" : "expired_notfound"})

            # Change email
            user.email = request.session.get("temp_new_email")
            user.save()

            # Unset session variable
            del request.session["temp_new_email"]

            return JsonResponse({"ok" : 1})
        else:
            return JsonResponse({"error" : "error"})
    else :
        return HttpResponseNotAllowed("Method not allowed")

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
                return HttpResponse("match")

            context = {}

            # Get users current email and password
            user_id = request.session.get("user_id")
            if users.objects.filter(user_id=user_id).exists():
                user = users.objects.get(user_id=user_id)
                context["user"] = user
            else:
                return HttpResponse("error")

            # Check if old password is the same as new password
            old_password_hash = user.password
            if check_password(new_password, old_password_hash):
                return HttpResponse("same")

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
                return HttpResponse("error")

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
            return HttpResponse("error")
    else :
        return HttpResponseNotAllowed("Method not allowed")

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
                return JsonResponse({"error" : "error"})

            # Delete expired codes
            unix_now = int(time.time())
            recovery_codes.objects.filter(expire__lt=unix_now).delete()

            # Check that new email session variable exists
            if 'temp_new_password' not in request.session:
                return JsonResponse({"error" : "error"})

            # Get users current email
            user_id = request.session.get("user_id")
            if users.objects.filter(user_id=user_id).exists():
                user = users.objects.get(user_id=user_id)
                email = user.email
            else:
                return JsonResponse({"error" : "error"})

            # Check if code exists in database
            if not recovery_codes.objects.filter(recovery_code=code, email=email).exists():
                return JsonResponse({"error" : "expired_notfound"})

            # Change password
            user.password = request.session.get("temp_new_password")
            user.save()

            # Unset session variable
            del request.session["temp_new_password"]

            return JsonResponse({"ok" : 1})
        else:
            return JsonResponse({"error" : "error"})
    else :
        return HttpResponseNotAllowed("Method not allowed")

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

        # Exclude any users in your friend list, users you have sent a request to and yourself
        for user in query_users:
            friend_uid = user.user_id
            if str(friend_uid) == user_id:
                continue
            elif friend_list.objects.filter(user_id_1=user_id, user_id_2=friend_uid).exists():
                continue
            elif pending_friends.objects.filter(outgoing=user_id, incoming=friend_uid).exists():
                continue
            else:
                result_users.append(user)

        # Pass into context
        context = {}
        context["users"] = result_users
        context["query"] = query

        return render(request, "friends/add_friends_result.html", context)
    else:
        return HttpResponseNotAllowed("Method not allowed")

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
                return JsonResponse({"error" : "noexist"})
        except:
            return JsonResponse({"error" : "noexist"})

        # Check if user is already in friend list
        if friend_list.objects.filter(user_id_1=user_id, user_id_2=friend_user_id).exists():
            return JsonResponse({"error" : "already_friends"})
        
        # Check if user has already sent a friend request to this user
        if pending_friends.objects.filter(outgoing=user_id, incoming=friend_user_id).exists():
            return JsonResponse({"error" : "alreadysent"})
        
        # Check if user is yourself
        if user_id == friend_user_id:
            return JsonResponse({"error" : "yourself"})
        
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
        return HttpResponseNotAllowed("Method not allowed")