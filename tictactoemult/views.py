from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def login(request):
    if request.method == "POST":
        data = request.POST
        username = data.get("username")
        password = data.get("password")
        return HttpResponse(username + password)
    else:
        return HttpResponseNotAllowed()
