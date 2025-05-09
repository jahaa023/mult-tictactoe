# Multiplayer Tic Tac Toe
Multiplayer Tic Tac Toe, also known as mult-tictactoe, is a multiplayer tic tac toe game built with Python Django with the Daphne WebSocket. It uses the MySQL Community database.
## Table of Contents
<a href="#Installation">Installation</a>
<br>
<a href="#Design">Design</a>
## Installation
>[!NOTE]
>The following tutorial shows you how to download and run the project on a Windows 11 machine.

Before starting, make sure you have Python 3.12.2 downloaded on the machine as well as MySQL Community Server and git.
Here are the links for all the downloads:
- <a href="https://www.python.org/downloads/release/python-3122/">Python 3.12.2</a>
- <a href="https://dev.mysql.com/downloads/mysql/">MySQL Community Server</a>
- <a href="https://git-scm.com/downloads/win">Git</a>

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
Inside the file, navigate to the <b>"ALLOWED_HOSTS"</b> variable, and add 127.0.0.1 and localhost to the array. This is to make sure it allows you to run the server locally.
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
Before we continue, we can set up the database. I recommend using the <a href="https://www.mysql.com/products/workbench/">MySQL Workbench</a> tool to log in to the database and run SQL queries.
Start of by logging in to the database as the root user with the password you made when you downloaded the database.
> [!NOTE]
> You might get a popup that says "Connection warning" and that MySQL workbench is incompatible. If you get this popup, just press "Continue anyway".

After you log into the workbench, you can run a query on it. In the query input, write the following:
```
CREATE DATABASE tictactoe;
```
After typing this in, press the lightning icon to run the query. 
If you get a green checkmark in the terminal below it, everything went well and you can close the workbench.
## Downloading the project
After you have created the database, we can now download the project from GitHub. Create a temporary directory somewhere on your computer in CMD.
```
mkdir C:\path\to\temp\directory
```
Then we can git clone the files into this directory
```
git clone https://github.com/jahaa023/mult-tictactoe C:\path\to\temp\directory
```
After all the files have been downloaded, we need to move the files into our Django project. We can do this with PowerShell. Type the following into CMD.
```
powershell.exe Copy-Item -Path C:\path\to\temp\directory\* -Destination C:\path\to\your\directory -Force -Recurse
```
This command will move the files from the GitHub into the directory and overwrite any existing files. Make sure to include the backslash and asterisk at the end.
Now we can delete the temporary directory.
```
del /S /Q C:\path\to\temp\directory\*
```
After this, we can download all the pip dependensies. Make sure your CMD is running inside the virtual environment during these steps.
We start off by cd'ing into our directory.
```
cd C:\path\to\your\directory
```
Then we can install all the requirements with the following command:
```
pip install -r requirements.txt
```
If you get an error during this step, try running CMD as an administrator and doing it again.
After this step, we can run a Django migration to create all the tables we'll need in the database. Type the following command:
```
python manage.py makemigrations
```
After that, type in the following command:
```
python manage.py migrate
```
Then we can finally run the server:
```
python manage.py runserver
```
If you get an error during this step, you can try to change the port to something else. Replace <port> with a port of your choosing.
```
python manage.py runserver <port>
```
If you get the following in your terminal, you have been successfull.
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
<date and time>
Django version 5.1.4, using settings 'tictactoe.settings'
Starting ASGI/Daphne version 4.1.2 development server at http://127.0.0.1:<port>/
Quit the server with CTRL-BREAK.
```
To stop the server, press CTRL and C at the same time in the terminal.

## Design
The only font on the website used is Roboto. But the Roboto font is used with diffrent properties like opacity, thickness and so on.<br>
The website also uses a very simple color pallette, consisting of a grey-ish white, a light black and a dark red and some other variations of these colors as well as a green:
| Color             | Hex Code   | Preview   |
|------------------|------------|-----------|
| Primary Red       | `#810D0D`  | ![](assets/primary-red.png) |
| Primary Black     | `#212121`  | ![#212121](https://via.placeholder.com/20/212121/000000?text=+) |
| Background White  | `#e6e6e6`  | ![#e6e6e6](https://via.placeholder.com/20/e6e6e6/000000?text=+) |
| Cancel Grey       | `#646464`  | ![#646464](https://via.placeholder.com/20/646464/000000?text=+) |
| Warning Red       | `#d44848`  | ![#d44848](https://via.placeholder.com/20/d44848/000000?text=+) |
| Accept Green      | `#257e25`  | ![#257e25](https://via.placeholder.com/20/257e25/000000?text=+) |

