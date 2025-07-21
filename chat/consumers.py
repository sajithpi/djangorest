import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.db.models import Q
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from . models import Connected, Chat, RoomChat, User, UserProfile
from better_profanity import profanity
from django.utils import timezone




class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
    
        print(f"NotificationConsumer=>Connecting to room: {self.room_name}, group: {self.room_group_name}")

        # Join room group
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        
        
        print(f"Disconnected Notification Chat Room, Room:{self.room_name}")
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message",'default')
        username = text_data_json["username"]
        notification_type = text_data_json.get("notification_type","normal")
        room_id = text_data_json.get("room_id")
        room_message_unread_count = 0
        
        
        if notification_type == 'chat':
            print(f"notification_type is chattt")
            room_message_unread_count = await sync_to_async(
                Chat.objects.filter(sender__user__username = username, room=room_id, is_read = False).count
            )()
        
        
        print(f"room_message_unread_count:{room_message_unread_count} message:{message}, room:{self.room_name}")
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "room_id":room_id, "message": message,"username":username, "notification_type":notification_type, "room_message_unread_count":room_message_unread_count}
        )
       


    # Receive message from room group
    async def chat_message(self, event):
        message = event.get("message")
        username = event.get("username")
        notification_type = event.get("notification_type")
        room_message_unread_count = event.get("room_message_unread_count")
        room_id   = event.get("room_id")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message,"username":username, "chat_room":room_id,"notification_typeeee":notification_type, "room_message_unread_count":room_message_unread_count}))
        
        
        
class ChatConsumer(AsyncWebsocketConsumer):
    
    profanity.load_censor_words()

    @database_sync_to_async
    def connect_user(self, room_name, channel_name):
        self.user = self.scope['user']
        room = RoomChat.objects.get(id=room_name)
        if self.user:
            try:
                connected = Connected.objects.get(user=self.user, room=room)
            except Connected.DoesNotExist:
                Connected.objects.create(user=self.user, room=room, channel_name=channel_name)
        return None

    @database_sync_to_async
    def disconnect_user(self, room_name, channel_name):
        room = RoomChat.objects.get(id=room_name)
        self.user = self.scope['user']
        try:
            connected = Connected.objects.get(user=self.user, room=room, channel_name=channel_name)
            connected.delete()
        except Connected.DoesNotExist:
            pass
        return None

    @database_sync_to_async
    def read_message(self, room, receiver_profile):
        self.user = self.scope['user']
        if self.user == receiver_profile.user:
            chat = Chat.objects.filter(room=room, receiver=receiver_profile.user).last()
            if chat:
                chat.is_read = True
                chat.save()

    # Main Functions

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # connect user function will store the user as an actively connected user
        # await self.connect_user(room_name=self.room_name, channel_name=self.channel_name)
        print(f"ChatConsumer=>Connecting to room: {self.room_name}, group: {self.room_group_name}")
        await self.accept()
        self.send(text_data=json.dumps({
            'type': 'Connection Established',
            'message': 'You are now connected',
        }))

    async def disconnect(self, close_code):
        # Leave room group
        print(f"ChatConsumer=>Disconnected the room: {self.room_name}, group: {self.room_group_name}")
        # This function is used to delete the user from the connected users from the active room
        # await self.disconnect_user(room_name=self.room_name, channel_name=self.channel_name)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
    
        text_data_json = json.loads(text_data)
        print(f"ChatConsumer=>{text_data_json}")
        message = text_data_json['message']
        room_id = text_data_json['room_id']
        sender_user = text_data_json['sender_user']
        received_user = text_data_json['received_user']
        sender_profile_pic = text_data_json['sender_profile_pic']
        receiver_profile_pic = text_data_json['receiver_profile_pic']
        type = text_data_json.get('type','text')
        file = text_data_json['file']
        timestamp = text_data_json['timestamp']
        print(f"MY MESSAGE:{message}")
        censored_message = profanity.censor(message)
        censored_message = str(message)
        room = await database_sync_to_async(RoomChat.objects.get)(id=room_id)

        sender_user = await database_sync_to_async(User.objects.get)(username=sender_user)
        sender_user_profile = await database_sync_to_async(UserProfile.objects.get)(user__username=sender_user)

        received_user = await database_sync_to_async(User.objects.get)(username=received_user)
        received_user_profile = await database_sync_to_async(UserProfile.objects.get)(user__username=received_user)
        encrypted_message  = room.encrypt_content(censored_message, room.encryption_key)
        chat = Chat(
            content=encrypted_message,
            sender=sender_user_profile,
            receiver=received_user_profile,
            room=room,
            photo = file,
            type=type,
        )
        await database_sync_to_async(chat.save)()

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': censored_message,
                'sender_user': sender_user.username,
                'room_id': room_id,
                'received_user': received_user.username,
                'sender_profile_pic':sender_profile_pic,
                'receiver_profile_pic':receiver_profile_pic,
                'file':file,
                'timestamp':timestamp,
            }
        )
        # Send a response to the sender
        response_message = "Your message was successfully received and processed."
        await self.send(text_data=json.dumps({
            'type': 'response_message',
            'sender_user': sender_user.username,
            'message': censored_message,
            'sender_profile_pic':sender_profile_pic,
            'receiver_profile_pic':receiver_profile_pic,
            'file':file,
            'timestamp':timestamp,
        }))
        
        # # Inside ChatConsumer.receive after saving the message
        # await self.channel_layer.send(
        #     f"notification_{received_user.username}",  # This should match the group/channel name in ChatNotificationConsumer
        #     {
        #         "type": "send.notification",
        #         "sender_user": sender_user.username,
        #         "received_user": received_user.username,
        #         "message": censored_message,
        #         "room_id": room_id,
        #     }
        # )

    # Receive message from room group
    async def chat_message(self, event):
        full_text = event['message']
        message = full_text[:575]
        sender_user = event['sender_user']
        room_id = event['room_id']
        received_user = event['received_user']
        sender_profile_pic = event['sender_profile_pic']
        receiver_profile_pic = event['receiver_profile_pic']
        file = event['file']
        timestamp = event['timestamp']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_user': sender_user,
            'room_id': room_id,
            'received_user': received_user,
            'sender_profile_pic':sender_profile_pic,
            'receiver_profile_pic':receiver_profile_pic,
            'file':file,
            'timestamp':timestamp,
            
        }))

        print("room id from chat message:", room_id)
        print("received_user:", received_user)
        # This function will store the message as seen if the receiver has seen the sent message
        room = await database_sync_to_async(RoomChat.objects.get)(id=room_id)
        receiver = await database_sync_to_async(User.objects.get)(username=received_user)
        receiver_profile = await database_sync_to_async(UserProfile.objects.get)(user=receiver)
        await self.read_message(room, receiver_profile)
        
    async def response_message(self, event):
        # Handle the response message type if needed
        message = event['message']
        sender_profile_pic = event['sender_profile_pic']
        # receiver_profile_pic = event['receiver_profile_pic']
        # You can process or log the response message here if necessary
        print("Response message:", message)