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
from rest_framework.exceptions import APIException, AuthenticationFailed
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .register import register_social_user, register_social_user_for_android
import json
# Create your views here.

class GoogleSocialAuthView(generics.GenericAPIView):
    
    permission_classes = [AllowAny]
    
    
    serializer_class = GoogleSocialAuthSerializer

    def post(self, request):
        device = request.headers.get('device','web')
        """

        POST with "auth_token"

        Send an idtoken as from google to get user information

        """
        try:
            serializer = self.serializer_class(data=request.data, context={'device': device})
            serializer.is_valid(raise_exception=True)
            data = ((serializer.validated_data)['auth_token'])
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status = status.HTTP_401_UNAUTHORIZED)
    
class FacebookSocialAuthView(generics.GenericAPIView):

    # serializer_class = FacebookSocialAuthSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Parse the JSON string
            # data = json.loads(request.data)
            auth_token = request.data.get('auth_token')
            platform = request.headers.get('platform','web')
            # auth_token = json.loads(auth_token)
           
            
            if platform == 'android':
                    auth_token = json.loads(auth_token)
                    message = register_social_user_for_android(
                    provider='facebook',
                    user_id=auth_token['userID'], 
                    name=auth_token['name'],
                    )
            else:
                message = register_social_user(
                        provider='facebook',
                        user_id=auth_token['userID'], 
                        email= auth_token['email'], 
                        name=auth_token['name'],
                        )
            print(f"auth_token:{auth_token}")
            
            return Response({'status':True,'message':'Registration Using Facebook Successfully', 'data':message}, status=status.HTTP_200_OK)
        except AuthenticationFailed as e:
            return Response(str(e), status= status.HTTP_400_BAD_REQUEST)
        except json.JSONDecodeError as e:
            return Response({'status':False,'error': f'Invalid auth_token format, {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response(f"ERROR:{str(e)}",status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status':False,'error': f'An error occurred during user registration, {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            