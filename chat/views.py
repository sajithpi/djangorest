from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from django.utils import timezone
from . models import RoomChat, Chat
from accounts.models import User, UserProfile
from django.db.models import Q
from rest_framework import status, generics
import json



# Create your views here.
class chatRoom(GenericAPIView):
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('room_id', openapi.IN_QUERY, description="ID of the room", type=openapi.TYPE_INTEGER, required=True),
        ],
         responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'message': openapi.Schema(type=openapi.TYPE_STRING),
                            'photo': openapi.Schema(type=openapi.TYPE_STRING),
                            'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            'sender_user': openapi.Schema(type=openapi.TYPE_STRING),
                            'sender_user_profile_photo': openapi.Schema(type=openapi.TYPE_STRING),
                            'received_user': openapi.Schema(type=openapi.TYPE_STRING),
                            'received_user_profile_photo': openapi.Schema(type=openapi.TYPE_STRING),
                            'is_read': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        },
                    ),
                ),
                examples={
                    "application/json": [
                        {
                            "message": "Hello!",
                            "photo": "http://example.com/photo.jpg",
                            "timestamp": "2023-11-17T12:00:00Z",
                            "sender_user": "sender_username",
                            "sender_user_profile_photo": "http://example.com/sender_photo.jpg",
                            "received_user": "receiver_username",
                            "received_user_profile_photo": "http://example.com/receiver_photo.jpg",
                            "is_read": True
                        },
                        # Add more examples as needed
                    ]
                },
            ),
            404: openapi.Response(
                description="Room not found",
            ),
            500: openapi.Response(
                description="API Error",
            ),
            # Add more response codes as needed
        },
        tags=["Chat"],
        operation_summary="Get chat messages for a room",
        operation_description="Retrieve a list of chat messages for a specific room.",
    )
    def get(self, request):
        try:
            # Get the room_id from the request data
            room_id = request.data.get('room_id')
            
            # Retrieve the RoomChat object based on the room_id
            room = RoomChat.objects.get(id=room_id)
            
            # Retrieve all chat messages for the specified room
            chats = Chat.objects.filter(room=room)
            
            # Create a list to store formatted chat data
            chat_list = []

            # Iterate through each chat and format the data
            for chat in chats:
                user_chat = {}
                user_chat['message'] = chat.content if chat.content else ''  # Use an empty string if content is None
                user_chat['photo'] = chat.photo if chat.photo else ''  # Use an empty string if photo is None
                user_chat['timestamp'] = chat.timestamp
                user_chat['sender_user'] = chat.sender.user.username
                user_chat['sender_user_profile_photo'] = str(chat.sender.profile_picture)
                user_chat['received_user'] = chat.receiver.user.username
                user_chat['received_user_profile_photo'] = str(chat.receiver.profile_picture)
                user_chat['is_read'] = chat.is_read
                chat_list.append(user_chat)

            # Return the formatted chat data in the response
            return Response(chat_list, status=status.HTTP_200_OK)

        except RoomChat.DoesNotExist:
            # Handle the case where the specified room_id does not exist
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Handle other exceptions
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'receiver_user': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['receiver_user']
        ),
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'room_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            404: openapi.Response(
                description="Not Found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            500: openapi.Response(
                description="Internal Server Error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
        },
        tags=["Chat"],
        operation_summary="Create or retrieve chat room",
        operation_description="Create a new chat room or retrieve an existing one based on the specified receiver user.",
    )
    def post(self, request):
        try:
            # Get receiver_user from the request data
            receiver_user = request.data.get('receiver_user')

            # Get sender's user and profile
            sender = User.objects.get(username=request.user)
            sender_profile = UserProfile.objects.get(user=sender)

            # Get receiver's user and profile
            receiver = User.objects.get(username=receiver_user)
            receiver_profile = UserProfile.objects.get(user=receiver)

            # Check if receiver_user is provided
            if receiver_user:
                # Check if a room already exists between sender and receiver
                room = RoomChat.objects.filter(
                    (Q(senderProfile=sender_profile) & Q(receiverProfile=receiver_profile)) |
                    (Q(senderProfile=receiver_profile) & Q(receiverProfile=sender_profile))
                ).first()

                # If room exists, retrieve its id; otherwise, create a new room
                if room:
                    room_id = room.id
                else:
                    room = RoomChat.objects.create(senderProfile=sender_profile, receiverProfile=receiver_profile)
                    room_id = room.id

                return Response({'room_id': room_id}, status=status.HTTP_200_OK)

            else:
                # If receiver_user is not provided, return a bad request response
                return Response({'error': 'Receiver user is required'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            # Handle the case where the specified user (sender or receiver) does not exist
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except UserProfile.DoesNotExist:
            # Handle the case where the profile for the specified user (sender or receiver) does not exist
            return Response({'error': 'UserProfile not found'}, status=status.HTTP_404_NOT_FOUND)

        except RoomChat.DoesNotExist:
            # Handle the case where the specified room does not exist
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Handle other exceptions
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class GetChatRooms(GenericAPIView):
    
    @swagger_auto_schema(
        operation_summary="Get User Rooms",
        operation_description="Get a list of chat rooms for the authenticated user.",
        responses={
            200: openapi.Response("Successful response",  schema=openapi.Schema(type='object', properties={"Rooms": [{"username": "example_user", "profile_pic": "example_url"}]})),
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
        },
        tags=['Chat']
    )
    def get(self, request):
        """
        Get a list of chat rooms for the authenticated user.

        Returns:
            Response: A JSON response containing the list of chat rooms.
        """
        try:
            # Retrieve the authenticated user and their profile
            user = User.objects.get(username=self.request.user)
            user_profile = UserProfile.objects.get(user=user)

            # Query for chat rooms involving the authenticated user
            rooms = RoomChat.objects.filter(Q(senderProfile=user_profile) | Q(receiverProfile=user_profile)).all()

            # Create a list of room dictionaries for the API response
            rooms_list = []
            for room in rooms:
                room_dict = {}
                room_user = room.senderProfile if room.senderProfile != user_profile else room.receiverProfile
                room_dict['username'] = room_user.user.username
                room_dict['profile_pic'] = str(room_user.profile_picture)
                rooms_list.append(room_dict)

            # Return the list of rooms in the API response
            return Response({"Rooms": rooms_list}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response("User not found", status=status.HTTP_401_UNAUTHORIZED)
        except UserProfile.DoesNotExist:
            return Response("User profile not found", status=status.HTTP_401_UNAUTHORIZED)
        except RoomChat.DoesNotExist:
            return Response("Chat rooms not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(f"An error occurred: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)