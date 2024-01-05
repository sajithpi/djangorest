from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from .serializers import UserSerializers, ResetPasswordEmailSerializer , SetNewPasswordSerializer, InterestSerializer, TestimonialSerializer
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.generics import GenericAPIView
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http  import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework.parsers import MultiPartParser
from .otp import send_otp_via_mail, send_otp_whatsapp, welcome_email, send_forgot_password_mail
from .utils import Util
from .models import User, UserProfile, CoverPhoto, Interest, UserTestimonial, EmailTemplate
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction
from django.conf import settings
from django.utils import timezone
import json
from datetime import datetime
from django.conf import settings
import threading
import pytz
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage, PageNotAnInteger
# Create your views here.

now = timezone.now()    # Get the current time 

class RegisterView(GenericAPIView):
    
    parser_classes = (MultiPartParser,)
    
    def post(self, request):
        try:
            serializer = UserSerializers(data=request.data, partial = True)
            serializer.is_valid(raise_exception=True)
            
            device = request.headers.get('device','web')
            
            # Extract cover photos from request data
            cover_photos_data = request.FILES.getlist('cover_photos')
            
            # Extract cover photos from request data
            profile_photo_data = request.FILES.get('profile_photo')
            
            # Extract the first cover photo if available
            # profile_photo_data = cover_photos_data[0] if cover_photos_data else None

            # Extract the interests data from request data as a list
            interests_data = json.loads(request.data.get('interests', '[]')) # Use getlist to retrieve a list 
            print(f"request data:{request.data}")
            with transaction.atomic():
                # Save the user
                user = serializer.save()
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
                    print(f"interests_data:{interests_data}")
                    if device == 'web':
                        interests_data = json.loads(interests_data)
                    for interest_name in interests_data:
                        print(f"interest_name:{interest_name}")
                        if device == 'web':
                            interest = Interest.objects.get(name=interest_name)
                        else:
                            interest= Interest.objects.get(id=interest_name)
                        if interest:
                            user.interests.add(interest)
                # else:
                #                 # Update user interests
                #     if 'interests' in request.data:
                #         print(f"interest data json:{request.data.get('interests')}")
                #         interests_data = request.data.get('interests', '[]')
                #         # interests_data = request.data.get('interests', '[]')
                #         if interests_data:
                #             interests_data = json.loads(interests_data)
                #             for interest_name in interests_data:
                #                 print(f"interest_name:{interest_name}")
                #                 interest= Interest.objects.get(id=interest_name)
                #                 if interest:
                #                     # user.user_ interests.add(interest)
                #                     user.interests.add(interest)
                            
                threading.Thread(target=welcome_email, args=(serializer.data['email'], serializer.data['username'],'register')).start()

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
        tags=["authentication"]
    )

    def post(self, request):
        try:

            otp = request.data.get('otp')
            email = request.data.get('email')
            type = request.data.get('type') #login, account_active
            print(f"otp:{otp} email:{email} type:{type}")
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
                print(f"user login otp:{user.login_otp} otp:{otp}, now:{settings.NOW}, otp validity:{user.login_otp_validity}")
                if user.login_otp != otp:
                    return Response(f"OTP is invalid", status=status.HTTP_403_FORBIDDEN)
                if user.login_otp_validity < settings.NOW:
                    return Response(f"Otp validity expired", status=status.HTTP_403_FORBIDDEN)
                user.has_2fa_passed = True
                user.login_status = True
                print(f"user password:{user.password}")
                user.save()
                refresh = RefreshToken.for_user(user)
                return Response({'status':'success','message':'Login otp verification successful', 'refresh_token':str(refresh),
                    'access_token':str(refresh.access_token), 'has_2fa_enabled':user.has_2fa_enabled, 'is_admin':user.is_admin}, status=status.HTTP_200_OK)
        except User.DoesNotExist as e:
            return Response(f"User does't exist with this email", status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"error:{e}")
            return Response(f"'error:{e}",status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class sendOTP(GenericAPIView):
    
    permission_classes = [AllowAny]  
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'type': openapi.Schema(type=openapi.TYPE_STRING, description='Type (e.g., login, account_active)'),
                'method': openapi.Schema(type=openapi.TYPE_STRING, description='Method (whatsapp or email)'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of user'),
            }
        ),
        responses={
            200: "Success",
        },
        tags=["authentication"]
    )
    
    
    def put(self, request):
        type = request.data.get('type')
        method = request.data.get('method')
        email = request.data.get('email')
        # print(f"user:{self.request.user.id}")
        user = User.objects.get(email = email)
        email = user.email
        print(f"email:{email}")
        print(f"method:{method}")
        if method == 'whatsapp':
            message = send_otp_whatsapp()
            return Response(message)
        elif method == 'email':
            send_otp_via_mail(email=email, username = user.username, type=type)
            return Response(f"{type} Otp sent into your email")
        
class LogoutView(GenericAPIView):
    @swagger_auto_schema(
        responses={
            200: "User Logout Successful",
        },
    )
    def put(self, request):
        user = User.objects.get(id = request.user.id)
        # token = RefreshToken(request.data.get('token'))
        # token.blacklist()
        user.has_2fa_passed = False
        user.login_status = False
        user.login_otp = None
        user.login_otp_validity = None
        print(f"TIME:{settings.NOW}")
        
        # Get the current time using settings.NOW
        current_time = settings.NOW
        
        # Extract and format the date and time components
        formatted_datetime = current_time.strftime('%Y-%m-%d %H:%M:%S')

        print(f"formatted_datetime:{formatted_datetime}")
        user.last_login = formatted_datetime
        # timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        user.save()
        return Response({'status':'True','  message':'User Logout Successful'}, status=status.HTTP_200_OK)
    
    
class ForgotPassword(GenericAPIView):
    def post(self, request):
        pass
class RequestPasswordResetEmail(GenericAPIView):
    """
    An endpoint for requesting a password reset email.

    Use this endpoint to request a password reset email. It will send an email with a link to reset the password.

    """
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='The email address of the user.'),
            },
            required=['email']
        ),
        responses={
            200: "Success. An email will be sent to the user.",
            400: "Bad request. Invalid email provided.",
            404: "User with the provided email not found."
        },
        tags=["authentication"]
    )
    def post(self, request):
        
        serializer = ResetPasswordEmailSerializer(data = request.data)
        email = request.data['email']

        if User.objects.filter(email=email).exists():
                user =  User.objects.get(email__exact=email)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                current_site = get_current_site(request=request).domain
                current_site = f'{settings.USER_URL}/reset-password/{uidb64}/{token}'
                # relativeLink = reverse('password_reset_confirm', kwargs={'uidb64':uidb64, 'token':token})
                absurl = current_site
                
                resetPasswordTemplate = EmailTemplate.objects.get(type = 'reset_password')
                resetPasswordTemplate_Content = resetPasswordTemplate.content.replace('{{company_name}}', 'Dating App').replace('{{username}}', user.username).replace('{{reset_link}}',absurl )
                email_from = settings.DEFAULT_FROM_EMAIL
                message = f'Password Reset'
                # email_body = 'Hello, \n Use link below to reset your password \n' + absurl
                send_forgot_password_mail(resetPasswordTemplate.subject,message, email_from, user.email, resetPasswordTemplate_Content)
                # threading.Thread(target=send_forgot_password_mail, args=(resetPasswordTemplate.subject, email_from, user.email,  resetPasswordTemplate_Content)).start()
                # data = {'email_body':email_body, 'to_email':user.email,
                #         'email_subject':'Reset your password'}
                # Util.send_mail(data)
        else:
            return Response({'Error':'Email does not Exists in this system'}, status=status.HTTP_404_NOT_FOUND)

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
        


class Testimonial(GenericAPIView):
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['description'],
            properties={
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Testimonial description'),
            },
        ),
        responses={
            200: openapi.Response('Testimonial created successfully'),
            400: openapi.Response('Bad Request, description is required'),
            404: openapi.Response('User does not exist'),
        },
        operation_description=" Create a new testimonial",
        tags=['Testimonial']
    )
    
    
    def post(self, request):
        try:
            print(f"USER:{request.user}")
            user = User.objects.get(username = request.user)
            user_profile = UserProfile.objects.get(user = user)
            
            description = request.data.get('description')
            if description:
                testimonial = UserTestimonial.objects.create(user = user_profile, description = description)
                return Response({"success": "Testimonial created successfully."}, status=status.HTTP_200_OK)
            return Response({'warning':'you have to add description'})
        
        except User.DoesNotExist:
              return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
   
   
   
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['testimonial_id', 'status'],
            properties={
                'testimonial_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Testimonial ID'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Testimonial status', enum=["0:Pending", "1:Accepted","2:Rejected"]),
                # openapi.Parameter('device', openapi.IN_HEADER, description="Device type", type=openapi.TYPE_STRING, enum=["web", "mobile"]),
            },
        ),
        responses={
            200: openapi.Response('Testimonial updated successfully'),
            400: openapi.Response('Bad Request, testimonial_id and status are required'),
            404: openapi.Response('User does not exist or testimonial not found'),
        },
        operation_description="Update Testimonial Status",
        tags=['Testimonial']
    )  
    
    
      
    def put(self, request):
        try:
            user = User.objects.get(username = request.user)
            if user.is_admin:
                
                testimonial_id = request.data.get('testimonial_id', [])
                print(f"TESTIMONIAL IDS:{testimonial_id}")
                request_status = request.data.get('status') 
        
                if testimonial_id and request_status:
                    testimonial = UserTestimonial.objects.filter(id__in = testimonial_id)
                    
                    testimonial.update(status = request_status) 
                    return Response(f'Testimonial updated successfully',status=status.HTTP_200_OK)
                else:
                    return Response({f'warning':'you have to pass request_status, testimonial_id'})
                
        except Exception as e:
            print(f"ERROR:{e}")
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
 


                
class GetTestimonialsView(GenericAPIView):
    
    
    authentication_classes = []  # Explicitly set no authentication
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('type', openapi.IN_HEADER, type=openapi.TYPE_STRING, required=False, description='Testimonial status type (0:pending, 1:accepted, 2:rejected)'),
        ],
        responses={
            200: openapi.Response('Testimonials retrieved successfully'),
            400: openapi.Response('Bad Request, an error occurred'),
            403: openapi.Response('Forbidden, user is not an admin'),
        },
        operation_description="  Retrieve testimonials based on the provided status type.",
        tags=['Testimonial'],
    )  
    
    
    def get(self, request):
        try:
            # user = User.objects.get(username = request.user)
            try:
                type = request.headers['type']
                
                rowsPerPage = request.headers.get('rowsperpage',0)
                currentPage = request.headers.get('page',0)
                if int(type) != 4:
                    testimonials = UserTestimonial.objects.filter(status = type)
                else:
                    testimonials = UserTestimonial.objects.all()
                count = testimonials.count()
                if rowsPerPage and currentPage: 
                    paginator = Paginator(testimonials, rowsPerPage)
                    
                    try:
                        testimonials = paginator.page(currentPage)
                    except EmptyPage:
                        return Response("Page not found", status=status.HTTP_404_NOT_FOUND)
                    except PageNotAnInteger:
                        return Response("Invalid page number", status=status.HTTP_400_BAD_REQUEST)
                    
            except KeyError as e:
                 testimonials = UserTestimonial.objects.all()
            
         
                
            
            print(f"COUNT:{count}")
            # serializer = TestimonialSerializer(data =testimonials, many = True)
            
            # serializer.is_valid()
            
            testimonial_list = []
            for testimonial in testimonials:
                testimonial_dict = {}
                testimonial_dict['id'] = testimonial.id
                testimonial_dict['user'] = testimonial.user.user.username
                testimonial_dict['profile_picture'] = str(testimonial.user.profile_picture)
                # testimonial_dict['location'] = 
                testimonial_dict['description'] = testimonial.description
                testimonial_dict['status'] = testimonial.status
                testimonial_dict['location'] = testimonial.user.city
                testimonial_list.append(testimonial_dict)                
            
            return Response({'count':count,'data':testimonial_list}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"ERROR:{e}")
            return Response(f"error:{e}",status=status.HTTP_400_BAD_REQUEST)
        
class PasswordReset(GenericAPIView):
    
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password1': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password2': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['password', 'new_password1', 'new_password2'],
        ),
        responses={
            200: "Password updated successfully",
            400: "Your Entered New password is not matching or Entered Password is not correct, please enter correct password",
        },
        operation_summary="Update Password",
        operation_description="Update the user's password.",
        tags=['account']
    )
    def put(self, request):
        user = User.objects.get(username = request.user)
        entered_password = request.data.get('password')
        new_password1 = request.data.get('new_password1')
        new_password2 = request.data.get('new_password2')
        if new_password1 != new_password2:
            return Response(f"Your Entered New password is not matching", status=status.HTTP_400_BAD_REQUEST)
        
        hashed_password = make_password(entered_password)
        if check_password(entered_password, user.password):
            user.set_password(new_password1)
            user.save()
            return Response("Password updated successfully", status=status.HTTP_200_OK)
        
        return Response("Entered Password is not correct, please enter correct password", status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    