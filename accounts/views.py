from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from .serializers import UserSerializers, ResetPasswordEmailSerializer , SetNewPasswordSerializer, InterestSerializer
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
from .otp import send_otp_via_mail, send_otp_whatsapp
from .utils import Util
from .models import User, UserProfile, CoverPhoto, Interest
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction
from django.conf import settings
from django.utils import timezone
import json
# Create your views here.

now = timezone.now()    # Get the current time 

class RegisterView(GenericAPIView):
    
    parser_classes = (MultiPartParser,)
    
    def post(self, request):
        try:
            serializer = UserSerializers(data=request.data, partial = True)
            serializer.is_valid(raise_exception=True)
            
            # Extract cover photos from request data
            cover_photos_data = request.FILES.getlist('cover_photos')
            
            # Extract cover photos from request data
            profile_photo_data = request.FILES.get('profile_photo')
            
            # Extract the first cover photo if available
            # profile_photo_data = cover_photos_data[0] if cover_photos_data else None

            # Extract the interests data from request data as a list
            interests_data = json.loads(request.data.get('interests', '[]')) # Use getlist to retrieve a list 
            
            with transaction.atomic():
                # Save the user
                user = serializer.save()
                send_otp_via_mail(email=serializer.data['email'], type='register')
                # Associate cover photos with the user's profile if provided
                if cover_photos_data:
                    user_profile = UserProfile.objects.get(user=user)
                    for image_data in cover_photos_data:
                        CoverPhoto.objects.create(user_profile=user_profile, image=image_data)
                        
                # If a profile photo was provided, set it as the profile picture
                if profile_photo_data:
                    user_profile = UserProfile.objects.get(user=user)
                    user_profile.profile_picture = profile_photo_data
                    user_profile.save()

                # Add interests
                if interests_data:
                    for interest_name in interests_data:
                        interest = Interest.objects.get(name=interest_name)
                        if interest:
                            user.interests.add(interest)

                return Response({'status': True, 'message': 'Registration Successful'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Handle other exceptions (e.g., database errors, file upload errors)
            print(f"Error in registration:{e}")
            return Response({'status': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class VerifyAccount(GenericAPIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description='The OTP'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='The email'),
                'type': openapi.Schema(type=openapi.TYPE_STRING, description='Type (login or account_active(for account activation))'),
            }
        ),
        responses={
            200: "Account Verified Successfully",
            400: "Bad Request",
            403: "Forbidden",
            500: "Internal Server Error",
        },
    )
    def post(self, request):
        try:

            otp = request.data.get('otp')
            email = request.data.get('email')
            type = request.data.get('type') #login, account_active
            
            user = User.objects.filter(email = email).first()
            print(f"user:{user}")
            if type == 'account_active':
                if not user:
                    return Response(f"{'status':false, 'message':'Enter a valid email'}", status=status.HTTP_400_BAD_REQUEST)
                if user.register_otp != otp:
                    return Response(f"{'status':false, 'message':'Enter a valid otp'}", status=status.HTTP_400_BAD_REQUEST)
                user.is_verified = True
                user.save()
                return Response(f"Account Verified Successfully",status=status.HTTP_200_OK)
            elif type == 'login':
                print(f"user login otp:{user.login_otp} otp:{otp}")
                if user.login_otp != otp:
                    return Response(f"OTP is invalid", status=status.HTTP_403_FORBIDDEN)
                if user.login_otp_validity < now:
                    return Response(f"Otp validity expired", status=status.HTTP_403_FORBIDDEN)
                user.has_2fa_passed = True
                user.login_status = True
                user.save()
                return Response({'status':'success','message':'Login otp verification successful'}, status=status.HTTP_200_OK)
        except User.DoesNotExist as e:
            return Response(f"User does't exist with this email", status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"error:{e}")
            return Response(f"'error:{e}",status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class sendOTP(GenericAPIView):
    

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'type': openapi.Schema(type=openapi.TYPE_STRING, description='Type (e.g., login, account_active)'),
                'method': openapi.Schema(type=openapi.TYPE_STRING, description='Method (whatsapp or email)'),
            }
        ),
        responses={
            200: "Success",
        },
    )
    def post(self, request):
        type = request.data.get('type')
        method = request.data.get('method')
        print(f"user:{self.request.user.id}")
        user = User.objects.get(id = request.user.id)
        email = user.email
        print(f"email:{email}")
        print(f"method:{method}")
        if method == 'whatsapp':
            message = send_otp_whatsapp()
            return Response(message)
        elif method == 'email':
            send_otp_via_mail(email=email, type=type)
            return Response(f"{type} Otp sent into your email")
        
class LogoutView(GenericAPIView):
    @swagger_auto_schema(
        responses={
            200: "User Logout Successful",
        },
    )
    def post(self, request):
        user = User.objects.get(id = request.user.id)
        # token = RefreshToken(request.data.get('token'))
        # token.blacklist()
        user.has_2fa_passed = False
        user.login_status = False
        user.login_otp = None
        user.login_otp_validity = None
        user.save()
        return Response({'status':'True','  message':'User Logout Successful'}, status=status.HTTP_200_OK)
class ForgotPassword(GenericAPIView):
    def post(self, request):
        pass
class RequestPasswordResetEmail(GenericAPIView):
    def post(self, request):
        
        serializer = ResetPasswordEmailSerializer(data = request.data)
        email = request.data['email']

        if User.objects.filter(email=email).exists():
                user =  User.objects.get(email__exact=email)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                current_site = get_current_site(request=request).domain
                relativeLink = reverse('password_reset_confirm', kwargs={'uidb64':uidb64, 'token':token})
                absurl = 'http://'+current_site+relativeLink
                email_body = 'Hello, \n Use link below to reset your password \n' + absurl
                data = {'email_body':email_body, 'to_email':user.email,
                        'email_subject':'Reset your password'}
                Util.send_mail(data)


        return Response({'success':'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
    
class PasswordTokenCheckAPI(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'Error':'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
                
            return Response({'success':True, 'message':'Crediantials Valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)
            
        except DjangoUnicodeDecodeError as Error:
            return Response({'Error':'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
            
class SetNewPasswordAPI(GenericAPIView):

    def patch(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        return Response({'success':True, 'message':'Password Reset Success'}, status=status.HTTP_200_OK)
    
        
class IntrestListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]  # Use AllowAny permission to allow unauthenticated access
    
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    
class InterestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    
class CheckUserExists(APIView):
    def get(self, request):
        email = request.data.get('email', None)
        
        if not email:
            return Response({'message':'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'message':'User with this email already exists'}, status=status.HTTP_200_OK)
        else:
            return Response({'message':'User with this email not exists'}, status=status.HTTP_200_OK)
        

