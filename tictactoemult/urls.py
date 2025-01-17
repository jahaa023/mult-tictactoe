from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('login', views.login),
    path('main', views.main),
    path('create_account' , views.create_account),
    path('create_account_form_handler', views.create_account_form_handler),
    path('username_validate', views.username_validate),
    path('account_recovery', views.account_recovery),
    path('account_recovery_email', views.account_recovery_email),
    path('account_recovery_inputcode', views.account_recovery_inputcode),
    path('account_recovery_code', views.account_recovery_code),
    path('account_recovery_final', views.account_recovery_final),
    path('reset_password', views.reset_password),
    path('logout', views.logout),
    path('settings', views.settings),
    path('edit_profile', views.edit_profile),
    path('editprofile_savechanges', views.editprofile_savechanges),
    path('profilepic_upload', views.profilepic_upload),
    path('profilepic_crop', views.profilepic_crop),
    path('profilepic_cropped_upload', views.profilepic_cropped_upload),
    path('display_profile/<str:uid>/', views.display_profile, name='uid'),
    path('personal_information', views.personal_information),
    path('change_email_modal', views.change_email_modal),
    path('change_email_modal_confirm', views.change_email_modal_confirm),
    path('change_password_modal', views.change_password_modal),
    path('change_password_modal_confirm', views.change_password_modal_confirm),
    path('friends', views.friends)
]
