from django.urls import path, include
from . views import chatRoom, GetChatRooms, StickersListCreateView, SendMessageView

urlpatterns = [
    path('user-room',chatRoom.as_view(), name='user-room'),
    path('get-chat-rooms', GetChatRooms.as_view(), name='get-chat-rooms'),
    path('custom-stickers',StickersListCreateView.as_view(),name='custom-stickers'),
    path('send-message',SendMessageView.as_view(),name='send-message'),
]