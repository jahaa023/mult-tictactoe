# Multiplayer Tic Tac Toe
Multiplayer Tic Tac Toe, also known as mult-tictactoe, is a multiplayer tic tac toe game built with Python Django with the Daphne WebSocket. It uses the MySQL Community database.

## Installation
>[!NOTE]
>The following tutorial shows you how to download and run the project on a Windows 11 machine.

Before starting, make sure you have Python 3.12.2 downloaded on the machine as well as MySQL Community Server and git.
Open CMD and make a directory to put the project in. 
```
mkdir C:\path\to\your\directory
```
After the directory has been made, create a Python virtual environment inside of it.
```
python -m venv C:\path\to\your\directory
```
Then, cd into the new directory
```
cd C:\path\to\your\directory
```
Then activate the virtual environment by starting the "activate" batch file.
```
start .\Scripts\activate.bat
```
You should then see the name of your directory in brackets.
```
(directory_name) C:\path\to\your\directory
```
We need to start by setting up a Django project to then later integrate our project into.
First, pip install Django.
```
pip install Django
```
Now we need to create a Django project. Start by cd'ing into the parent folder.
```
cd ..
```
Then we need to create the Django project inside of the directory we made. Change out <my_directory> with the name of the folder you created
```
django-admin startproject tictactoe <my_directory>
```
Your directory should now look like this:
```
<my_directory>\
  manage.py
  .gitignore
  pyvenv.cfg
  Include
  Lib
  Scripts
  tictactoe\
    __init__.py
    asgi.py
    settings.py
    urls.py
    wsgi.py
```
Then we need to create the actual app inside of this Django project. First, cd back into the directory
```
cd \path\to\my\directory
```
And then run this command to create the tictactoe app
```
py manage.py startapp tictactoemult
```
There should now be a new folder in your directory with these files and folders:
```
tictactoemult\
  __init__.py
  admin.py
  apps.py
  models.py
  tests.py
  views.py
  migrations\
    __init__.py
```
Before we continue, we need to configure some settings inside of the <b>settings.py</b> file in the tictactoe directory.
Inside the file, navigate to the <b>"ALLOWED_HOSTS"</b> varible, and add 127.0.0.1 and localhost to the array. This is to make sure it allows you to run the server locally.
```
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
```
Then, navigate to the <b>"INSTALLED APPS"</b> variable and add 'daphne' and 'tictactoemult' to it
```
INSTALLED_APPS = [
    'daphne',
    'tictactoemult',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
]
```
Then scroll down to the <b>"TEMPLATES"</b> variable, and add "BASE_DIR / 'templates'" inside of the brackets next to 'DIRS:'
```
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```
Then, under the <b>"WSGI_APPLICATION"</b> variable, type the following line:
```
ASGI_APPLICATION = "tictactoe.asgi.application"
```
After that, we need to configure our database connection. Scroll down to the <b>"DATABASES"</b> variable, and replace it with the following. Replace the details with your own.
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tictactoe',
        'USER': 'root',
        'PASSWORD': '<my_db_password>',
        'HOST':'localhost',
        'PORT':'3306',
    }
}
```
Finally, scroll down to the very bottom of the file and add these lines:
```
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```
Next, open the <b>asgi.py</b> file and replace the contents with the following:
```
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tictactoe.settings")
django_asgi_app = get_asgi_application()

from tictactoemult.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
```
After that, open the <b>urls.py</b> file and replace the contents with the following:
```
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tictactoemult.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

```
Then, inside of the <b>tictactoemult</b> directory, create a file named <b>custom_settings.py</b>.
To this file, add the following and replace details with your own:
```
RESEND_API_KEY = "<yourapikey>"
```
> [!WARNING]
> This variable is for the API key for the Resend service (https://resend.com). This service is used on the website to send emails containing recovery codes for accounts. Note that you need a domain to set up the Resend API and that the website might not function properly without it.

Then finally, create a folder in the same directory as the <b>tictactoe</b> and <b>tictactoemult</b> folder called <b>media</b>. This folder is where files like images are temporarily uploaded.

## Setting up the database
