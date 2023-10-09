from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import FollowSerializer
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
from .models import Follower
from django.shortcuts import get_object_or_404
from accounts.models import User, UserProfile
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import json
# Create your views here.

class FollowUser(GenericAPIView):

    def post(self, request):
        print(f"request data:{request.data}")
        serializer = FollowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message':'success', 
                         'description':'User follow action success'},
                         status=status.HTTP_200_OK)
    
class GetFollowData(GenericAPIView):
    def post(self,request):
        user_id = request.data.get('user_id')
        
        # Ensure the user exists or return a 404 response if not found
        user = get_object_or_404(User, id=user_id)
        user_profile = UserProfile.objects.get(user = user)
        # Calculate total followers and total following for the user
        total_followers = Follower.objects.filter(following=user_profile).count()
        total_following = Follower.objects.filter(followed_by=user_profile).count()
        
        # Get the list of users following the current user
        users_followed_by_current_user = Follower.objects.filter(following=user_profile).values_list('followed_by', flat=True)

        #fetch username, and user profile picture of each user in the users_following_current_user list
        followers_data = UserProfile.objects.filter(user__id__in=users_followed_by_current_user).values('user__username','user__id','profile_picture')

        #get the list of users where the current user following
        following_users_of_current_user = Follower.objects.filter(following=user_profile).values_list('following',flat=True)

        #fetch username, and user profile picture of each user in the users_following_current_user list
        following_data = UserProfile.objects.filter(user__id__in=following_users_of_current_user).values('user__username','user__id','profile_picture')

        return Response({
            'message': 'Success',
            'description': 'User follow action success',
            'total_followers': total_followers,
            'total_following': total_following,
            'users_followed_by_users': followers_data,
            'following_data':following_data,
        }, status=status.HTTP_200_OK)