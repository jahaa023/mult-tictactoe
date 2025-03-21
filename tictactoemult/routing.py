from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/matchmaking/", consumers.matchmakingConsumer.as_asgi()),
    path("ws/match/<str:room_name>/", consumers.matchConsumer.as_asgi())
]