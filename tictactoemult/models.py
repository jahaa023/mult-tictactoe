from django.db import models
import uuid

# Create your models here.

# Model to create users table
class users(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    username = models.CharField(max_length=30)
    nickname = models.CharField(max_length=30, null=True)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=40)
    joindate = models.CharField(max_length=64, default='0')
    description = models.CharField(max_length=300, default='No description')
    profile_picture = models.CharField(max_length=128, default='defaultprofile.jpg')
    stayloggedin_token = models.UUIDField(default=uuid.uuid4,editable=False)

# Model for recovery codes table for account recovery
class recovery_codes(models.Model):
    email = models.CharField(max_length=40)
    recovery_code = models.IntegerField()
    expire = models.IntegerField()
