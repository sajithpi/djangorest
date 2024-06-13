from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # re_path(r"ws/notification/(?P<room_name>\w+)/$", consumers.NotificationConsumer.as_asgi()),
    re_path(r"djangoapi/ws/notification/(?P<room_name>\w+)/$", consumers.NotificationConsumer.as_asgi()),
    re_path(r"djangoapi/ws/chatNotification/(?P<room_name>\w+)/$", consumers.ChatNotificationConsumer.as_asgi()),
    re_path(r"djangoapi/ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
]