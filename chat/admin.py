from django.contrib import admin
from chat.models import Chat, RoomChat, Connected
# Register your models here.

class ChatAdmin(admin.ModelAdmin):
    list_display = ['sender','receiver','content','photo','timestamp','is_read']

class RoomChatAdmin(admin.ModelAdmin):
    list_display = ['id','sender_username','receiver_username']
    
    def sender_username(self, obj):
        return obj.senderProfile.user.username
    
    def receiver_username(self, obj):
        return obj.receiverProfile.user.username
class ConnectedAdmin(admin.ModelAdmin):
    list_display = ['user','room_id','channel_name','connect_date']

admin.site.register(Chat,ChatAdmin)
admin.site.register(RoomChat,RoomChatAdmin)
admin.site.register(Connected,ConnectedAdmin)