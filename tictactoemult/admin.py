from django.contrib import admin
from .models import users, recovery_codes

# Register your models here.
admin.site.register(users)
admin.site.register(recovery_codes)