from django.shortcuts import render
from rest_framework.views import APIView
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
from .utils import Util
from .models import User, UserProfile, CoverPhoto, Interest
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import json
# Create your views here.

class RegisterView(GenericAPIView):
    
    parser_classes = (MultiPartParser,)
    
    def post(self, request):
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
        
        user = serializer.save()
        
        # Associate cover photos with the user's profile if provided
        if cover_photos_data:
            user_profile = UserProfile.objects.get(user=user)
            for image_data in cover_photos_data:
                CoverPhoto.objects.create(user_profile = user_profile, image = image_data)
                
                
        # If a profile photo was provided, set it as the profile picture
        if profile_photo_data:
            user_profile = UserProfile.objects.get(user=user)
            user_profile.profile_picture = profile_photo_data
            user_profile.save()
        print(f"interests_data:{interests_data}")
        for interest_name in interests_data:
            interest_name = interest_name.strip()
            print(f"interest_name:{interest_name}")
            interest= Interest.objects.get(name=interest_name)
            if interest:
                # user.user_ interests.add(interest)
                user.interests.add(interest)
        
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'status':True,'message':'Registration Successful'}, status=status.HTTP_201_CREATED)
    
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


        return Response({'success':'We have sent you a link to reset your passwors'}, status=status.HTTP_200_OK)
    
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
            