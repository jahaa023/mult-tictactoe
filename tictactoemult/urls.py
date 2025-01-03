from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('login', views.login),
    path('main', views.main),
    path('create_account' , views.create_account),
    path('create_account_form_handler', views.create_account_form_handler),
    path('username_validate', views.username_validate)
]
