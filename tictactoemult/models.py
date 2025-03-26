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
    left = models.UUIDField(default="00000000000000000000000000000000") # User id of person who left
    user_id_1_ping = models.IntegerField(default=0) # Unix timestamp for last update from user id 1
    user_id_2_ping = models.IntegerField(default=0) # Unix timestamp for last update from user id 2
    round = models.IntegerField(default=1) # Keeps track of which round it is
    match_status = models.JSONField(default=dict) # Includes diffrent stats about match
    final_win = models.JSONField(default=dict) # User id of person who won the entire match and reason to why they won

# Model for leaderboard table
class leaderboard(models.Model):
    user_id = models.UUIDField() # Which user the stats are for
    wins = models.IntegerField(default=0) # How many wins the user has
    losses = models.IntegerField(default=0) # How many losses the user has
    matches_played = models.IntegerField(default=0) # How many matches the user has played
    win_loss = models.FloatField(default=0.0) # Win loss ratio
