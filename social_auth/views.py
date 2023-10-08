from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import  GoogleSocialAuthSerializer, FacebookSocialAuthSerializer
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
from accounts.models import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import json
# Create your views here.

class GoogleSocialAuthView(generics.GenericAPIView):
    
    serializer_class = GoogleSocialAuthSerializer

    def post(self, request):
        
        """

        POST with "auth_token"

        Send an idtoken as from google to get user information

        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return Response(data, status=status.HTTP_200_OK)
    
class FacebookSocialAuthView(generics.GenericAPIView):

    serializer_class = FacebookSocialAuthSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return Response(data, status=status.HTTP_200_OK)