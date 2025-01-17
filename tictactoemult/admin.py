from django.contrib import admin
from .models import users, recovery_codes, friend_list, pending_friends

# Register your models here.
admin.site.register(users)
admin.site.register(recovery_codes)
admin.site.register(friend_list)
admin.site.register(pending_friends)