from django.shortcuts import render
from django.http import HttpResponse
from .forms import LoginForm

# Create your views here.

def index(request):
    # The default index.html page, with a form for logging in
    context = {}
    context['form'] = LoginForm()
    return render(request, 'index.html', context)

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

def main(request):
    return HttpResponse("test")

def create_account(request):
    return render(request, 'create_account.html')