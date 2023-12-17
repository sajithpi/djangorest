from django.contrib import admin
from chat.models import Chat, RoomChat, Connected, Sticker
# Register your models here.

class ChatAdmin(admin.ModelAdmin):
    list_display = ['room_id','sender','receiver','content','photo','timestamp','is_read']
    list_filter = ['room_id']
    search_fields = ['room_id']

class RoomChatAdmin(admin.ModelAdmin):
    list_display = ['id','sender_username','receiver_username','encryption_key']
    
    def sender_username(self, obj):
        return obj.senderProfile.user.username
    
    def receiver_username(self, obj):
        return obj.receiverProfile.user.username
class ConnectedAdmin(admin.ModelAdmin):
    list_display = ['user','room_id','channel_name','connect_date']
    
class StickerAdmin(admin.ModelAdmin):
    list_display = ['id','photo']
    
admin.site.register(Chat,ChatAdmin)
admin.site.register(Sticker, StickerAdmin)
admin.site.register(RoomChat,RoomChatAdmin)
admin.site.register(Connected,ConnectedAdmin)