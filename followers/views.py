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
        
        # Calculate total followers and total following for the user
        total_followers = Follower.objects.filter(following=user).count()
        total_following = Follower.objects.filter(followed_by=user).count()
        
        # Get the list of users following the current user
        users_following_current_user = Follower.objects.filter(following=user).values_list('followed_by', flat=True)

        return Response({
            'message': 'Success',
            'description': 'User follow action success',
            'total_followers': total_followers,
            'total_following': total_following,
            'users_following_current_user': users_following_current_user,
        }, status=status.HTTP_200_OK)