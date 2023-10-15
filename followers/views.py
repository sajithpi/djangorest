from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import FavoriteSerializer
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http  import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework.parsers import MultiPartParser
from .models import Favorite, Like
from django.shortcuts import get_object_or_404
from accounts.models import User, UserProfile
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import json
# Create your views here.
"""_summary_
    First two classes for Favorites
    Returns:
        _type_: Favorite 
"""
class AddRemoveFavorite(GenericAPIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="The ID of the user to favorite/unfavorite."
                ),
            },
            required=['user'],
        ),
        responses={
            200: "Favorite/unfavorite action was successful",
            400: "Bad request or user is already favorited/unfavorited",
            500: "Internal server error",
        },
    )
    def post(self, request):
        """
        Favorite/Unfavorite a user.
        """
        try:
            print(f"request data:{request.data}")
            user = request.data.get('user')
            favored_by = UserProfile.objects.get(user__id = request.user.id)
            user = UserProfile.objects.get(user = user)
            # favoured_user = UserProfile.objects.get(user = favored_by)
            exists = Favorite.objects.filter(user = user, favored_by = favored_by).first()
            if exists:
                exists.delete()
                return Response({'status':'True', 
                                'message': f"{favored_by.user.username} is already Favorited {user.user.username} so user in unfavored this user",
                                'action':f"{favored_by.user.username}' is unfavored {user.user.username}"
                                }, 
                                status=status.HTTP_200_OK)
            favorite = Favorite.objects.create(user = user, favored_by = favored_by)
            favorite.save()
            print(f"user:{user} favored_user:{request.user}")
            return Response({'message':'Success', 
                            'description':f"{favored_by.user.username} is Favorited {user.user.username} Successfully"},
                            status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
        
class GetFavoriteUsers(GenericAPIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            200: "Successful response with admire count and favorite user data",
            404: "User not found",
        },
    )
    
    def post(self, request):
        """
        Get favorite users and admire count. Note:User Must be login
        """
        user_id = request.user.id
        
        # Ensure the user exists or return a 404 response if not found
        user = get_object_or_404(User, id=user_id)
        user_profile = UserProfile.objects.get(user = user)
        # Calculate total followers and total following for the user
        admire_count = Favorite.objects.filter(user=user_profile).count()
        my_favorites = Favorite.objects.filter(favored_by=user_profile).count()
        
        # Get the list of users following the current user
        my_admire_list = Favorite.objects.filter(user=user_profile).values_list('favored_by', flat=True)

        #fetch username, and user profile picture of each user in the users_following_current_user list
        my_admires_data = UserProfile.objects.filter(user__id__in=my_admire_list).values('user__username','user__id','profile_picture')

        #get the list of users where the current user following
        my_favorite_list = Favorite.objects.filter(favored_by=user_profile).values_list('user',flat=True)

        #fetch username, and user profile picture of each user in the users_following_current_user list
        my_favorite_data = UserProfile.objects.filter(user__id__in=my_favorite_list).values('user__username','user__id','profile_picture')

        return Response({
            'message': 'Success',
            'description': 'User follow action success',
            'admire_count': admire_count,
            'my_favorites': my_favorites,
            'my_admires_data': my_admires_data,
            'my_favorite_data':my_favorite_data,
        }, status=status.HTTP_200_OK)
    
"""_summary_: Classes For LIking
"""
class LikeDislike(GenericAPIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="The ID of the user to like/dislike."
                ),
            },
            required=['user'],
        ),
        responses={
            200: "Like/Dislike action was successful",
            400: "Bad request or user is already Liked",
            500: "Internal server error",
        },
    )
    def post(self, request):
        """
        Like/Dislike a user.
        """
        try:
            print(f"request data:{request.data}")
            user = request.data.get('user')
            liked_by = UserProfile.objects.get(user__id = request.user.id)
            user = UserProfile.objects.get(user = user)
            # favoured_user = UserProfile.objects.get(user = liked_by)
            exists = Like.objects.filter(user = user, liked_by = liked_by).first()
            if exists:
                exists.delete()
                return Response({'status':'True', 
                                'action':f"{liked_by.user.username}' is disliked {user.user.username}"
                                }, 
                                status=status.HTTP_200_OK)
            like = Like.objects.create(user = user, liked_by = liked_by)
            like.save()
            print(f"user:{user} favored_user:{request.user}")
            return Response({'message':'Success', 
                            'description':f"{liked_by.user.username} is liked {user.user.username} Successfully"},
                            status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   

class GetLikeUsers(GenericAPIView):
    
    def post(self, request):
        
        user_id = request.user.id
        
        # Ensure the user exists or return a 404 response if not found
        user = get_object_or_404(User, id=user_id)
        user_profile = UserProfile.objects.get(user = user)
        # Calculate total likes you got and your likes 
        admire_count = Like.objects.filter(user=user_profile).count()
        my_likes = Like.objects.filter(liked_by=user_profile).count()
        
        # Get the list of users liked the current user
        my_admire_list = Like.objects.filter(user=user_profile).values_list('liked_by', flat=True)

        #fetch username, and user profile picture of each user in the users_liked current_user list
        my_admires_data = UserProfile.objects.filter(user__id__in=my_admire_list).values('user__username','user__id','profile_picture')

        #get the list of users where the current user liked
        my_like_list = Like.objects.filter(liked_by=user_profile).values_list('user',flat=True)

        #fetch username, and user profile picture of each user in the user liked  list
        my_like_data = UserProfile.objects.filter(user__id__in=my_like_list).values('user__username','user__id','profile_picture')

        return Response({
            'message': 'Success',
            'admire_count': admire_count,
            'my_likes': my_likes,
            'my_admires_users': my_admires_data,
            'my_like_data':my_like_data,
        }, status=status.HTTP_200_OK)
    