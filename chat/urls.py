from django.urls import path, include
from . views import chatRoom, GetChatRooms

urlpatterns = [
    path('user-room',chatRoom.as_view(), name='user-room'),
    path('get-chat-rooms', GetChatRooms.as_view(), name='get-chat-rooms')
]