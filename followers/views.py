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
from accounts.models import User, UserProfile, CoverPhoto, Interest
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