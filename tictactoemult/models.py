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
    banner_color = models.CharField(max_length=32, default="#969696")
    stayloggedin_token = models.UUIDField(default=uuid.uuid4,editable=False)
    ping = models.IntegerField(default=0)

# Model for recovery codes table for account recovery
class recovery_codes(models.Model):
    email = models.CharField(max_length=40)
    recovery_code = models.IntegerField()
    expire = models.IntegerField()

# Model for friend list
class friend_list(models.Model):
    user_id_1 = models.UUIDField() #User id 1 is friends with user id 2
    user_id_2 = models.UUIDField() #User id 2 is friends with user id 1
    became_friends = models.CharField(max_length=64) # Timestamp for when the invite was accepted

# Model for pending friends
class pending_friends(models.Model):
    outgoing = models.UUIDField() # User id who sent the invite
    incoming = models.UUIDField() # User id who received the invite
    sent = models.CharField(max_length=64) # Timestamp for when the invite was sent

# Model for matchmaking
class matchmaking(models.Model):
    user_id_1 = models.UUIDField() # Host of the match
    user_id_2 = models.UUIDField(default="00000000000000000000000000000000") # Person who joins the host

# Model for matches
class match(models.Model):
    user_id_1 = models.UUIDField() # Host of the match
    user_id_2 = models.UUIDField() # Person who joins the host
    turn = models.UUIDField() # User id of whos turn it is
    taken_slots = models.JSONField() # JSON of which slots on the board are taken
    room_name = models.CharField(max_length=16, default="0") # Name of the room
    timer = models.IntegerField(default=0) # Unix timestamp for when timer runs out
    x = models.UUIDField(default="00000000000000000000000000000000") # User id of person who is x
    o = models.UUIDField(default="00000000000000000000000000000000") # User id of person who is o