import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.db.models import Q
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from . models import Connected, Chat, RoomChat, User
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        print(f"message:{message}")
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message,"username":username}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message,"username":username}))
        
        
class ChatConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def connect_user(self, room_name, channel_name):
        self.user = self.scope['user']
        room = RoomChat.objects.get(id=room_name)
        if self.user:
            try:
                connected = Connected.objects.get(user=self.user, room=room)
            except:
                Connected.objects.get_or_create(user=self.user, room=room,channel_name = channel_name)
            
        else:
            pass
        return None
    @sync_to_async
    def disconnect_user(self, room_name, user, channel_name):
        room = RoomChat.objects.get(id = room_name)
        self.user = self.scope['user']
        user = []
        if self.user:
            try:
                get_object_or_404(Connected, Q(user=self.user), Q(room=room), Q(channel_name=channel_name))
            except:
                pass
            else:
                user = get_object_or_404(Connected, Q(user=self.user), Q(room=room), Q(channel_name=channel_name))
                user.delete()
        return None
    @sync_to_async
    def read_message(self, room, receiver):
        self.user = self.scope['user']
        print("room:",room.id)
        print("user:",self.user.username)
        print("receiver:",receiver.username)
        if self.user == receiver:
            chat = Chat.objects.filter(room = room, receiver = receiver).last()
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
        # connect user function will be store the user as activily connected user
        await self.connect_user(room_name=self.room_name,channel_name=self.channel_name)
        await self.accept()
        self.send(text_data=json.dumps({
            'type':'Connection Established',
            'message':'You are now connected',
        }))

    async def disconnect(self, close_code):
          # Leave room group
        print("disconnected")
        # This function use to delete the user from the connected users from the active room
        await self.disconnect_user(room_name=self.room_name, user=self.scope['user'], channel_name=self.channel_name)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        room_id = text_data_json['room_id']
        self.user_id = self.scope['user'].id
        # print("room_id:",room_id)
        print("message:",message)
        #Find room object

        room = await database_sync_to_async(RoomChat.objects.get)(id=room_id)
      
        # room = await database_sync_to_async(RoomChat.objects.get)(receiver=self.room_name)
        #Create new chat object

        sender_user = room.sender
        receiver_user = room.receiver
        # Changing sender and receiver values when new message sented
        if self.scope['user'].username == room.receiver:
            sender_user = room.receiver
            receiver_user = room.sender
            print("room sender_profile1:",sender_user)
            print("room receiver_profile1:",receiver_user)
            room.sender = sender_user
            room.receiver = receiver_user
            await database_sync_to_async(room.save)()
        elif self.scope['user'].username == room.sender:
            sender_user = room.sender
            receiver_user = room.receiver
            print("room sender_profile2:",sender_user)
            print("room receiver_profile2:",receiver_user)
            room.sender = sender_user
            room.receiver = receiver_user

            await database_sync_to_async(room.save)()
        received_user = await database_sync_to_async(User.objects.get)(username=receiver_user)
        chat = Chat(
            content = message,
            sender = self.scope['user'],
            receiver = received_user,
            room = room,
        )    
        await database_sync_to_async(chat.save)()


        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': self.user_id,
                'room_id':room_id,
                'receiver':room.receiver,
                # 'room_id' : room_id,
            }
        )


     # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']
        room_id = event['room_id']
        received_user = event['receiver']
         # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id,
            'room_id' : room_id,
        }))

        print("room id from chat message:",room_id)
        print("received_user:",received_user)
        # This function will store the message as seen if the receiver seen the sented message
        room = await database_sync_to_async(RoomChat.objects.get)(id=room_id)
        receiver = await database_sync_to_async(User.objects.get)(username=received_user)
        await self.read_message(room,receiver)

    