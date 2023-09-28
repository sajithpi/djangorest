from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializers, ResetPasswordEmailSerializer, SetNewPasswordSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http  import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from .models import User
# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class ForgotPassword(APIView):
    def post(self, request):
        pass
class RequestPasswordResetEmail(APIView):
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
    
class PasswordTokenCheckAPI(APIView):
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'Error':'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
                
            return Response({'success':True, 'message':'Crediantials Valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)
            
        except DjangoUnicodeDecodeError as Error:
            return Response({'Error':'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
            
class SetNewPasswordAPI(APIView):

    def patch(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        return Response({'success':True, 'message':'Password Reset Success'}, status=status.HTTP_200_OK)