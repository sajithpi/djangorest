from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from . models import User, UserProfile, CoverPhoto, Interest, Package, EducationType, RelationShipGoal, Religion, FamilyPlanChoice, DrinkChoice, Workout, Language, SmokeChoice, ProfilePreference, Notification, KycCategory, KycDocument, EmailTemplate, Configurations, CompanyData
from . serializers import UserSerializers, UpdateUserSerializer, PackageSerializer, UpdateUserProfileSerializer, CoverPhotoSerializer, UserProfileSerializer, ProfilePreferenceSerializerForMobile, InterestSerializer, CombinedSerializer, ProfilePreferenceSerializer, NotificationSerializer , CompanyDataSerializer, ConfigurationSerializer
from chat.models import RoomChat, Chat
from rest_framework import status, permissions
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from rest_framework.serializers import Serializer
from datetime import datetime
from user_agents import parse
from django.core import serializers
from django.conf import settings
from django.core.mail import send_mail
import json
from django.http import QueryDict
from followers.models import Favorite, Like, BlockedUser, Rating
from html import escape
import math
from geopy.geocoders import Nominatim
from rest_framework.exceptions import NotFound, ParseError
import requests
import threading
from bs4 import BeautifulSoup
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage, PageNotAnInteger
from rest_framework.mixins import CreateModelMixin
from django.utils import timezone

class TwoFactorAuthRequired(permissions.BasePermission):
    def has_permission(self, request, view):
        #check if the user has passed 2fa
        user = User.objects.get(id=request.user.id)
        if user.is_authenticated:
            if user.has_2fa_enabled and not user.has_2fa_passed:
                return False #Return false to deny the access
            return True
class Test(GenericAPIView):
    permission_classes = []
    def get(self, request):
        user_agent_string = request.META.get('HTTP_USER_AGENT')
        user_agent = parse(user_agent_string)


        
        print(f"user agent details:{user_agent}, agent device:{user_agent.browser.family}")
        os = user_agent.os.family
        pc_device = user_agent.device.family
        browser = user_agent.browser.family
        # device = user_agent.device.family
        print(f"os:{os}\npc_device:{pc_device}")


    
        print(f"browser:{browser}")
        return Response(f"User Agent:{user_agent} device:{user_agent.device} browser:{user_agent.browser.family}")

class GetUserData(GenericAPIView):
    permission_classes = (IsAuthenticated, TwoFactorAuthRequired)

    @swagger_auto_schema(
        operation_description="Get user data",  # Describe the operation
        responses={200: UserProfileSerializer},  # Define the response schema
        tags=["User"],  # Categorize the endpoint using tags
    )
    def get(self, request):
        # Get user agent details
        user_agent_string = request.META.get('HTTP_USER_AGENT')
        user_agent = parse(user_agent_string)
        print(f"user agent details:{user_agent}")

        # Get device details
        device = user_agent.device
        print(f"device:{device}")

        # Get client IP address
        client_ip = request.META.get('REMOTE_ADDR')
        print(f"my ip:{client_ip}")

        # Get browser details
        print(f"browser:{user_agent.browser.family}")

        # Get device from headers
        device_from_headers = request.headers.get('device', 'web')
        print(f"device:{device_from_headers}")

        # Get the user's profile
        user = self.request.user
        profile = UserProfile.objects.get(user=user)

        # Fetch user interests
        interests = profile.user.interests.all()

        # Serialize profile data with interests
        profile_serializer = UserProfileSerializer(profile, context={'device': device_from_headers})
        data = profile_serializer.data
        print(f"data:{data}")

        # Parse HTML tags to plain text using BeautifulSoup
        plain_text = ''
        if data['about_me']:
            soup = BeautifulSoup(data['about_me'], 'html.parser')
            plain_text = soup.get_text(separator=' ')
            print(f"DATA ABOUT ME SOUP:{plain_text}")

        # Add interests to the serialized data
        data['about_me'] = data['about_me'] if device_from_headers == 'web' and  data['about_me'] else plain_text
        data['interests'] = InterestSerializer(interests, many=True).data

        return Response(data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
    operation_description="Update user data",  # Describe the operation
    request_body=CombinedSerializer,  # Define the request body schema
    responses={200: "Success", 400: "Bad Request"},
    tags=["User"],  # Categorize the endpoint using tags
)
    def put(self, request):
        user = self.request.user

        user_agent_string = request.META.get('HTTP_USER_AGENT')
        user_agent = parse(user_agent_string)


        
        user_agent_string = request.META.get('HTTP_USER_AGENT')
        user_agent = parse(user_agent_string)

        user = self.request.user
        device = request.headers.get('device','web')
        # Create a mutable copy of request.data
        print(f"request data:{request.data}")
        
        if 'about_me' in request.data:
            html_content = request.data['about_me']
            if device == 'web':
                # escaped_html = escape(html_content)
                json_data = json.dumps(html_content)
                request.data['about_me'] = json_data
        # mutable_data = QueryDict(request.data.urlencode(), mutable=True)
        #Update fields in the User model if provided
        user_serializer = UpdateUserSerializer(user, data = request.data, partial = True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=400)
        
        # Update fields in the UserProfile model if provided
 
        try:
            profile = UserProfile.objects.get(user=user)
            if request.data.get('height'):
                height = request.data.get('height')[0] if device == 'mobile' else request.data.get('height')
                print(f"height type:{type(height)}")
                print(f"height:{height}")
                
                if height:
                    feet = height.get('feet',0)
                    print(f"feet:{feet}")
                    inches = height.get('inches',0)
                    cm = height.get('cm',0)
                    if not feet and not inches and not cm:
                        request.data['height'] = 0
                    
                    print(f"height:{height}, feet:{feet}, inches:{inches}")
                    if feet:
                        feet_in_cm = float(feet) * 30.48
                        inch_in_cm = float(inches) * 2.54
                        height = feet_in_cm + inch_in_cm
                        print(f"height:{height}")
                        request.data['height'] = round(float(height),2)
                    else:
                        request.data['height'] = cm 
                    
               
            request.data['is_edited'] = True
            print(f"data:{request.data}")
            profile_serializer = UpdateUserProfileSerializer(profile, data=request.data, partial = True)  # Use your UserProfile serializer
            if profile_serializer.is_valid():
                
                
                
                if 'profile_picture' in request.data:
                    old_profile_picture = profile.profile_picture
                    if old_profile_picture:
                        old_profile_picture.delete(save=False)
                    else:
                        print("profile picture not exist")
                
                
                #save languages
                language_data = request.data.get('languages',[])
                language_list = [item['value'] for item in language_data] if not device == 'mobile' else language_data
                # language_list = [item['value'] for item in language_data]
                profile.languages.clear()
                for language_value in language_list:
                    print(f"language value:{language_value}")
                    # language = Language.objects.get(name=language_value)
                    if device == 'mobile':
                        language = Language.objects.get(id = language_value)
                    else:
                        language = Language.objects.get(name=language_value)
                
                    print(f"language obj:{language}")
                    profile.languages.add(language)

                profile_serializer.save()
            else:
                return Response(profile_serializer.errors, status=400) # Return validation errors


            # Update user interests
            if 'interests' in request.data:
                print(f"interest data json:{request.data.get('interests')}")
                interests_data = request.data.get('interests', '[]')
                # interests_data = request.data.get('interests', '[]')
                if interests_data:
                    for interest_name in interests_data:
                        print(f"interest_name:{interest_name}")
                        interest_name = interest_name.strip()
                        interest= Interest.objects.get(name=interest_name)
                        if interest:
                            # user.user_ interests.add(interest)
                            user.interests.add(interest)
                
            return Response({'message':'User Profile updated successfully'})
        except UserProfile.DoesNotExist:
            return Response({'error':'UserProfile does not exist for this user.'}, status=404)
  
def get_country_and_city_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    print(f"aaa")
    print(f"latitude:{latitude} longitude:{longitude}")
    location = geolocator.reverse(f"{latitude}, {longitude}")
    if location.raw.get("address"):
        address = location.raw["address"]
        country = address.get("country")
        print(f"country: {country}")
        # Check for different keys that might contain city information
        city_keys = ["city", "town", "village"]
        for key in city_keys:
            city = address.get(key)
            if city and country:
                return {'city':city,
                        'country':country}

    return "City information not found"

def getCityAndCountry(latitude, longitude):
    count = 0
    country = ''
    city = ''
    try:
        country_and_city = get_country_and_city_from_coordinates(latitude, longitude)
        country = country_and_city.get('country')
        city = country_and_city.get('city')
    except AttributeError as e:
        if count == 0:
            new__longitude = float(longitude) * -1
            print(f"new__longitude:{new__longitude}")
            country_and_city = get_country_and_city_from_coordinates(latitude, new__longitude)
            country = country_and_city.get('country')
            city = country_and_city.get('city')
        else:
            country_and_city = get_country_and_city_from_coordinates(latitude * -1, longitude)
            country = country_and_city.get('country')
            city = country_and_city.get('city')
        count +=1
    finally:
        return {'city':city,
                'country':country}

class UpdateUserLocation(GenericAPIView):
    permission_classes = (IsAuthenticated,TwoFactorAuthRequired)

    def post(self, request):
        try:
            user = User.objects.get(username=self.request.user)
            user_profile = UserProfile.objects.get(user=user)
            if self.request.data.get('longitude') and self.request.data.get('latitude'):
                longitude =  self.request.data.get('longitude')
                latitude = self.request.data.get('latitude')
                user_profile.longitude = self.request.data.get('longitude')
                user_profile.latitude = self.request.data.get('latitude')
                cityAndProfle = getCityAndCountry(latitude,longitude)
                    
                # print(f"user_profile.country:{country}")
                print(f"user_profile.city:{cityAndProfle}")
                
                user_profile.city =  cityAndProfle.get('city')
                user_profile.country = cityAndProfle.get('country')
                user_profile.save()
                return Response('Location Updated Successfully', status=status.HTTP_200_OK)
            return Response('Location arguments missing',status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error in Location:{e}")
            return Response(f'Error in location updation:{str(e)}',status = status.HTTP_400_BAD_REQUEST)
# Calculate age based on date of birth
def calculate_age(date_of_birth):
    now = settings.NOW
    today = now
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    return age

def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    if not lat1 or not lon1 or not lat2 or not lon2:
        return 0
    
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Radius of the Earth in kilometers
    earth_radius = 6371.0  # Approximate value for Earth's radius

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c

    return round(distance,2)
lorem_ipsum = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""
class GetProfileDetails(GenericAPIView):
    
    permission_classes = (IsAuthenticated,TwoFactorAuthRequired)
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, description="User ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('device', openapi.IN_HEADER, description="Device type", type=openapi.TYPE_STRING, enum=["web", "mobile"]),
        ],
        responses={200: 'Success', 400: 'Bad Request', 404: 'Not Found'},
        tags=["User Profile"],
    )
    def get(self, request):
        username = request.GET.get('username')
        device = request.headers.get('device','web')
        
        if not username:
            return Response({"message": "Missing 'user_id' header"}, status=400)

        try:
            current_user = User.objects.get(id = request.user.id)
            current_user_profile = UserProfile.objects.get(user = current_user)
            user = User.objects.get(username=username)
            # user_profile = UserProfile.objects.filter(user=user).values('user__username', 'user__date_of_birth', 'user__interests', 'user__cover').first()
            profile = UserProfile.objects.get(user=user)
        
                # Fetch user interests
            interests = profile.user.interests.all()
            
            # Serialize profile data with interests
            profile_serializer = UserProfileSerializer(profile, context = {'device':device})
            
            
            data = profile_serializer.data
            print(f"data:{data}")
            # Add interests to the serialized data
            data['interests'] = InterestSerializer(interests, many=True).data
            favorite_status = True if Favorite.objects.filter(user=profile, favored_by=current_user_profile).first() else False
            like_status = True if Like.objects.filter(user=profile, liked_by=current_user_profile).first() else False
            block_status = True if BlockedUser.objects.filter(user=profile, blocked_by = current_user_profile).first() else False
            rating_users = [{'id':rating.cover_photo_id, 'rating':rating.rate_count} for rating in Rating.objects.filter(user = profile, rated_by = current_user_profile).all()]
            # Create a mapping from cover_photo_id to rating
            cover_photo_rating_map = {rating['id']: rating['rating'] for rating in rating_users}

            # Iterate through the cover photos and add the rating
            for cover_photo in data['cover_photos']:
                cover_photo_id = cover_photo['id']
                
                # Check if a rating exists for this cover photo ID
                if cover_photo_id in cover_photo_rating_map:
                    cover_photo['rating'] = cover_photo_rating_map[cover_photo_id]
                else:
                    # Handle the case where no rating is available for this cover photo
                    cover_photo['rating'] = None
            
            profile_data = {
                'id':data['user']['id'],
                'username':data['user']['username'],
                'about_me':lorem_ipsum,
                'age': calculate_age(datetime.strptime(data['user']['date_of_birth'], '%Y-%m-%d')) if user.showAge else False,
                'profile_picture':data['profile_picture'],
                'distance': haversine_distance(current_user_profile.latitude, current_user_profile.longitude, profile.latitude, profile.longitude),
                'interests':data['interests'],
                'cover_photos':data['cover_photos'],
                'favorite_status':favorite_status,
                'like_status':like_status,
                'block_status':block_status,
                          
            }
            
            return Response(profile_data, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

class getLoginUserData(GenericAPIView):
    def get(self, request):
        user = User.objects.get(username = self.request.user)
        user_profile = UserProfile.objects.get(user = user)
        data =  {'user_id':user.id ,'username':user.username, 'profile_picture':str(user_profile.profile_picture)}
        return Response(data, status=status.HTTP_200_OK)
    
class GetMyPreferences(GenericAPIView):
    @swagger_auto_schema(
        operation_description="Get user preferences",  # Describe the operation
        responses={200: ProfilePreferenceSerializer()},  # Define the response schema
        tags=["Preference"],  # Categorize the endpoint using tags
    )
    def get(self, request):
        device = request.headers.get('device','web')

        user_profile = UserProfile.objects.get(user = self.request.user)
        my_preferences = ProfilePreference.objects.get(user_profile = user_profile)
        if device == 'mobile':
            my_preference_serializer = ProfilePreferenceSerializerForMobile(my_preferences)
            return Response(my_preference_serializer.data, status=status.HTTP_200_OK)
        my_preference_serializer = ProfilePreferenceSerializer(my_preferences)
        # print(f"data:{my_preference_serializer.data}")
         # Customize the response format for the languages_choices field
        data = {}
        for field_name in my_preference_serializer.data:
            field_value = my_preference_serializer.data[field_name]
            
            if isinstance(field_value, list):
                data[field_name] = [{'label': value, 'value': value} for value in field_value]
            else:
                data[field_name] = [{'label': field_value, 'value': field_value}]

        return Response(data, status=status.HTTP_200_OK)

class UpdateProfilePhoto(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    
    
    @swagger_auto_schema(
        operation_description="Update profile photo",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'profile_picture': openapi.Schema(
                    type=openapi.TYPE_FILE,
                    description="The profile picture file to upload."
                ),
            },
            required=['profile_picture'],
        ),
        responses={200: "Success", 400: "Bad Request"},
        tags=["UserProfile"],
    )
    def put(self, request):
        user = self.request.user

        # Update fields in the UserProfile model if provided
        try:
            profile = UserProfile.objects.get(user=user)
            profile_serializer = UpdateUserProfileSerializer(profile, data=request.data, partial = True)  # Use your UserProfile serializer
            if profile_serializer.is_valid():
                if 'profile_picture' in request.data:
                    old_profile_picture = profile.profile_picture
                    if old_profile_picture:
                        old_profile_picture.delete(save=False)
                    else:
                        print("profile picture not exist")
                profile_serializer.save()
            else:
                return Response(profile_serializer.errors, status=400) # Return validation errors
            
        except UserProfile.DoesNotExist:
            return Response({'error':'UserProfile does not exist for this user.'}, status=404)
        return Response({'message':'User Profile updated successfully'})
    
    
class DeleteCoverPhoto(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    
    
    
    @swagger_auto_schema(
        operation_description="Delete cover photo",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'image_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="The ID of the cover photo to delete."
                ),
            },
            required=['image_id'],
        ),
        responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
        tags=["UserProfile"],
    )
    def put(self, request):
        user = self.request.user
        image_id = request.data.get('image_id',None)
        
        if image_id is None:
            return Response({'error': 'Image ID is required'}, status=status.HTTP_400_BAD_REQUEST) 
        
         # Update fields in the UserProfile model if provided
        try:
            profile = UserProfile.objects.get(user = user)
            cover_photo = CoverPhoto.objects.filter(user_profile = profile, id = image_id).first()
            if not cover_photo:
                return Response({'error': 'Cover photo not found'}, status=status.HTTP_404_NOT_FOUND)
            # Delete the cover photo file from storage
            cover_photo.image.delete(save=False)
            # Delete the corresponding database record)
            cover_photo.delete()
            return Response({'message': 'Cover photo deleted successfully'})

        except UserProfile.DoesNotExist:
            return Response({'error': 'UserProfile does not exist for this user.'}, status=status.HTTP_404_NOT_FOUND)


class CheckUserExists(GenericAPIView):
    serializer_class = Serializer  
    
    @swagger_auto_schema(
        operation_summary="Check if a user with a given email exists",
        manual_parameters=[
            openapi.Parameter('user_info', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="User_info address to check")
        ],
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Result message")
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                }
            ),
        },
        tags=["UserProfile"]
    )
    def post(self, request):
        user_info = request.data.get('user_info')
        
        if not user_info:
            return Response({'message':'user_info is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(Q(email=user_info) | Q(username = user_info)).exists():
            return Response({'message':'User with this info already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'User with this info not exists'}, status=status.HTTP_200_OK)
        
class RemoveUserInterestView(GenericAPIView):
    
    permission_classes = [IsAuthenticated,]
    
    
    @swagger_auto_schema(
        operation_summary="Remove a user's interest",
        operation_description="Remove a specific interest from the user's profile.",
        manual_parameters=[
            openapi.Parameter('interest_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="ID of the interest to remove", required=True),
        ],
        responses={
            status.HTTP_204_NO_CONTENT: "Interest removed successfully",
            status.HTTP_404_NOT_FOUND: "User or interest not found",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal server error",
        },
        tags=["interests"]
    )
    def put(self, request):
        try:
            
            user_id = request.user.id
            # interest_id = request.data.get('interest_id',None)
            # if not interest_id:
            #     return Response({'status':False, 'message':'interest should be passed'}, status=status.HTTP_204_NO_CONTENT)
            
            # user = User.objects.get(id=user_id)
            # interest = Interest.objects.get(id = interest_id)
            # user.interests.remove(interest)
            
            
                        # Update user interests
            # interests_data = json.loads(request.data.get('interest_id', '[]'))
            device = request.headers.get('device','web')
            interests_data = request.data.get('interest_id', [])
            print(f"interests_data:{interests_data}")
            user = User.objects.get(id=user_id)
            if interests_data:
                for interest_id in interests_data:
                    print(f"interest_id:{interest_id}")
                    if device == 'mobile':
                        interest= Interest.objects.get(name=interest_id)
                    else:
                        interest= Interest.objects.get(id=interest_id)
                    if interest:
                        # user.user_ interests.add(interest)                        
                        user.interests.remove(interest)
            
            return Response({'status': True, 'message': 'Interest removed successfully'}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            print(f"ERROR:{e}")
            return Response({'status': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except Interest.DoesNotExist:
            print(f"ERROR:{e}")
            return Response({'status': False, 'message': 'Interest not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f"ERROR:{e}")
            return Response({'status': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetPreferences(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    
    @swagger_auto_schema(
    operation_description="Get preference list",  # Describe the operation
    responses={200: UserProfileSerializer},  # Define the response schema
    tags=["Preference"],  # Categorize the endpoint using tags
    )
    def get(self, request):
        # Fetch data from each model
        interests = Interest.objects.all()
        drink_choices = DrinkChoice.objects.all()
        family_plan_choices = FamilyPlanChoice.objects.all()
        workouts = Workout.objects.all()
        religions = Religion.objects.all()
        relationship_goals = RelationShipGoal.objects.all()
        smoke_choices = SmokeChoice.objects.all()
        education_types = EducationType.objects.all()
        languages = Language.objects.all()

        api_type = request.headers.get('settingsType')
        # Get the value of a specific header
        # device = request.headers.get('device','web')
        device = request.headers.get('device','web')
        print(f"user agent:{device}")
        print(f"api_type:{api_type}")
        if api_type == 'settings':
              # Create dictionaries for each model's data
            interests_data = [{'id': interest.id, 'name': interest.name} for interest in interests]
            drink_choices_data = [{'id': choice.id, 'name': choice.name} for choice in drink_choices]
            family_plan_choices_data = [{'id': choice.id, 'name': choice.name} for choice in family_plan_choices]
            workouts_data = [{'id': workout.id, 'name': workout.name} for workout in workouts]
            religions_data = [{'id': religion.id, 'name': religion.name} for religion in religions]
            relationship_goals_data = [{'id': goal.id, 'name': goal.name} for goal in relationship_goals]
            smoke_choices_data = [{'id': choice.id, 'name': choice.name} for choice in smoke_choices]
            education_types_data = [{'id': education.id, 'name': education.name} for education in education_types]
            
            if device == 'mobile':
                languages_data = [{'id': language.id, 'name': language.name} for language in languages]
            else:
                languages_data = [{'label': language.name, 'value': language.name} for language in languages]
        else:
        
            # Create dictionaries for each model's data
            interests_data = [{'id': interest.id, 'name': interest.name} for interest in interests]
            drink_choices_data = [{'label': choice.name, 'value': choice.name} for choice in drink_choices]
            family_plan_choices_data = [{'label': choice.name, 'value': choice.name} for choice in family_plan_choices]
            workouts_data = [{'label': workout.name, 'value': workout.name} for workout in workouts]
            religions_data = [{'label': religion.name, 'value': religion.name} for religion in religions]
            relationship_goals_data = [{'label': goal.name, 'value': goal.name} for goal in relationship_goals]
            smoke_choices_data = [{'label': choice.name, 'value': choice.name} for choice in smoke_choices]
            education_types_data = [{'label': education.name, 'value': education.name} for education in education_types]
            # languages_data = [{'label': language.name, 'value': language.name} for language in languages]
            
            if device == 'mobile':
                languages_data = [{'id': language.id, 'name': language.name} for language in languages]
            else:
                languages_data = [{'label': language.name, 'value': language.name} for language in languages]

        # Create a response data dictionary
        data = {
            'interests': interests_data,
            'drink_choices': drink_choices_data,
            'family_plan_choices': family_plan_choices_data,
            'workouts': workouts_data,
            'religions': religions_data,
            'relationship_goals': relationship_goals_data,
            'smoke_choices': smoke_choices_data,
            'education_types': education_types_data,
            'languages': languages_data,
        }

        return Response(data, status=status.HTTP_200_OK)
    

class GetFollowers(GenericAPIView):
    def post(self, request):
        user = self.request.user
        print(f"user_id:{user.id}")
        user_profile = UserProfile.objects.get(user = user)

        return Response({'message':'success'}, status=status.HTTP_200_OK)


class UpdateProfilePreference(GenericAPIView):
        
        @swagger_auto_schema(
        operation_description="Update the user's profile preferences",
        request_body=ProfilePreferenceSerializer,
        responses={200: ProfilePreferenceSerializer, 400: "Bad Request"},
        tags=["Preference"],
        )
        def put(self, request):
            user = self.request.user
            
        
            user_profile = UserProfile.objects.get(user=user)
            try:
                print(f"user:{user} profile:{user_profile}")
                profile_preference = ProfilePreference.objects.get(user_profile = user_profile)
                
            except ProfilePreference.DoesNotExist:
                return Response({'detail':"ProfilePreference does't exist for this user"},status=status.HTTP_400_BAD_REQUEST)
            print(f"request.data:{request.data}")
            device = request.headers.get('device','web')
            self.update_choices(Language, request.data, 'languages_choices', 'languages_choices', device)
            self.update_choices(FamilyPlanChoice, request.data, 'family_choices', 'family_choices', device)
            self.update_choices(RelationShipGoal, request.data, 'relationship_choices', 'relationship_choices', device)
            self.update_choices(DrinkChoice, request.data, 'drink_choices', 'drink_choices', device)
            self.update_choices(Religion, request.data, 'religion_choices','religion_choices', device)
            self.update_choices(EducationType, request.data, 'education_choices', 'education_choices', device)
            self.update_choices(Workout, request.data, 'workout_choices', 'workout_choices', device)
            self.update_choices(SmokeChoice, request.data, 'smoke_choices', 'smoke_choices', device)
            # request.data['languages_choices'] = language_ids
            #Clear existing preferences
            profile_preference.family_choices.clear()
            profile_preference.drink_choices.clear()
            profile_preference.religion_choices.clear()
            profile_preference.education_choices.clear()
            profile_preference.relationship_choices.clear()
            profile_preference.workout_choices.clear()
            profile_preference.smoke_choices.clear()
            profile_preference.languages_choices.clear()
            # if device == 'mobile':
            serializer = ProfilePreferenceSerializer(profile_preference, data=request.data,  partial =True)
            # else:
            #      serializer = ProfilePreferenceSerializerForMobile(profile_preference, data=request.data,  partial =True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':"User Preference Updated Successfully", 'data':serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        def update_choices(self, model, data, choice_key, field_name, device):
            if device == 'web':
                if choice_key in data:
                    choice_list = data[choice_key]
                    print(f"choice_list{choice_list}")
                    choice_values = [choice.get('value','') for choice in choice_list]
                    print(f"choice_values:{choice_values}")
                    choice_id_mapping = {choice.name:choice.id for choice in model.objects.filter(name__in=choice_values)}
                    print(f"choice_id_mapping:{choice_id_mapping}")
                    choice_values_ids = [choice_id_mapping.get(value) for value in choice_values]
                    print(f"choice_values_ids:{choice_values_ids}")
                    
                    data[field_name] = choice_values
                    
                
            else:
                if choice_key in data:
                    choice_ids = data[choice_key]
                    choice_names = []

                    for choice_id in choice_ids:
                        choice_name = model.objects.filter(id=choice_id).values_list('name', flat=True).first()
                        if choice_name:
                            choice_names.append(choice_name)

                    data[choice_key] = choice_names



def get_blocked_users_data(user_profile):
        """
        Get blocked users. Note: User must be logged in.
        """    
        
        # Ensure the user exists or return a 404 response if 
        # user_profile = UserProfile.objects.get(user = user)
        
        my_blocked_user_count = BlockedUser.objects.filter(blocked_by=user_profile).count()

         # Get the list of users blocked the current user
        users_blocked_me = BlockedUser.objects.filter(user=user_profile).values_list('blocked_by', flat=True)

        #fetch username, and user profile picture of each user in the users blocked current_user list
        users_blocked__data = UserProfile.objects.filter(user__id__in=users_blocked_me).values('user__id')
        users_blocked__id = [user['user__id'] for user in users_blocked__data]
        #get the list of users where the current user blocked
        my_blocked_list = BlockedUser.objects.filter(blocked_by=user_profile).values_list('user',flat=True)

        #fetch username, and user profile picture of each user in the user liked  list
        my_blocked_users_data = UserProfile.objects.filter(user__id__in=my_blocked_list).values('user__id')
        my_blocked_users_id = [user['user__id'] for user in my_blocked_users_data]
        
        blocked_users = list(set(users_blocked__id + my_blocked_users_id))
        
        return blocked_users
    


class GetProfileMatches(GenericAPIView):
    @swagger_auto_schema(
        responses={
            200: "Success",
        },
        tags=["Preference"],
    )
    def get(self, request):
        # Retrieve the user's preferences
        user = self.request.user
        user_profile = UserProfile.objects.get(user=user)
        user_gender = user_profile.user.gender
        user_orientation = user_profile.user.orientation
        
        report_type = request.headers.get('type','normal')
    

        device = request.headers.get('device','web')
        print(f"USER {user} GENDER:{user_gender}, ORIENTATION:{user_orientation}")
        user_preferences = ProfilePreference.objects.get(user_profile=user_profile)
        print(f"user preferences:{user_preferences}")
        print(f"family preference:{user_preferences.family_choices.all()}")
        
        blocked_users = get_blocked_users_data(user_profile=user_profile)
        print(f"blocked users:{blocked_users}")
        user_orientation_filter = {
            ('M', 'Hetero'): 'F',
            ('M', 'Homo'): 'M',
            
            ('F', 'Hetero'): 'M',
            ('F', 'Homo'): 'F',

            ('TM', 'Hetero'): 'TF',
            ('TM', 'Homo'): 'TM',

            ('TF', 'Hetero'): 'TM',
            ('TF', 'Homo'): 'TF',
            
        }
        
        user_partner_gender_preference = user_orientation_filter.get((user_gender, user_orientation))
        print(f"user partner preference:{user_partner_gender_preference}")
        preferences_to_check = {
            'family_choices': 'family_plan',
            'drink_choices': 'drink',
            'religion_choices': 'religion',
            'education_choices': 'education',
            'relationship_choices': 'relationship_goals',
            'workout_choices': 'workout',
            'smoke_choices': 'smoke',
            'languages_choices': 'languages',
        }

        choice_count = len(preferences_to_check)
        
        # Create a dictionary to map field names to choices
        field_mapping = {
            'family_plan': user_preferences.family_choices,
            'drink': user_preferences.drink_choices,
            'religion': user_preferences.religion_choices,
            'education': user_preferences.education_choices,
            'relationship_goals': user_preferences.relationship_choices,
            'workout': user_preferences.workout_choices,
            'smoke': user_preferences.smoke_choices,
            'languages': user_preferences.languages_choices,
        }
        # Create a list to store preferences for each user
        preferences_list = []
        
        for queryset_attr, preference_key in preferences_to_check.items():
            queryset = getattr(user_preferences, queryset_attr).all()
            if queryset.exists():
                matched_preferences = [str(choice) for choice in queryset]
                user_preferences_dict = {
                    'preference_key': preference_key,
                    'matched_preferences': matched_preferences
                }
                preferences_list.append(user_preferences_dict)

        # Create a list of Q objects to match at least one preference in each category
        preferences_filters = []

        preference_fields = {
            'family_plan': 'family_choices',
            'drink': 'drink_choices',
            'religion': 'religion_choices',
            'education': 'education_choices',
            'relationship_goals': 'relationship_choices',
            'workout': 'workout_choices',
            'smoke': 'smoke_choices',
            'languages': 'languages_choices'
        }
            
        for preference, queryset_name in preference_fields.items():
            queryset = getattr(user_preferences, queryset_name).all()
            if queryset.exists():
                field_name = f"{preference}__in"
                preferences_filters.append(Q(**{field_name: queryset}))

        # Combine the Q objects using the OR operator (|)
        combined_filter = Q()
        for q_obj in preferences_filters:
            combined_filter &= q_obj
        # Create a Q object to represent the exclusion condition
        exclude_blocked_users = Q(user__id__in=blocked_users)

        # Query to find matching user profiles

        
        if user_orientation == 'Bi':
            
            matching_profiles = UserProfile.objects.filter(
            combined_filter & ~exclude_blocked_users,
            ~Q(user__id=user.id),
            user__orientation=user_orientation
            )
        else:
            matching_profiles = UserProfile.objects.filter(
            combined_filter & ~exclude_blocked_users,
            user__gender=user_partner_gender_preference,
            user__orientation=user_orientation
                )
            
        if report_type == 'adminReport':
              matching_profiles = UserProfile.objects.all()
              
              
        # Get unique user IDs from matching profiles
        unique_user_ids = matching_profiles.distinct()
        # Create a list to store user preferences
        preferences_list = []
        current_date = datetime.now()
        for profile in unique_user_ids:
            user_id = profile.user.id
            cover_photos = CoverPhoto.objects.filter(user_profile = profile)
            
            print(f"user_id:{user_id}")
            matches_count = 0
            preferences_by_user_id = {}
            preferences_by_user_id['id'] = profile.user.id
            preferences_by_user_id['username'] = profile.user.username
            if device == 'mobile':
                preferences_by_user_id['interests'] = [{'id':interests.id, 'name':interests.name }for interests in profile.user.interests.all()]
            else:    
                preferences_by_user_id['interests'] = [interests.name for interests in profile.user.interests.all()]
            if profile.user.date_of_birth:
                preferences_by_user_id['date_of_birth'] = profile.user.date_of_birth
                age = current_date.year - profile.user.date_of_birth.year - ((current_date.month, current_date.day) < (profile.user.date_of_birth.month, profile.user.date_of_birth.day)) 
                preferences_by_user_id['age'] = age if profile.user.showAge else False
            preferences_by_user_id['profile_picture'] = {
                'id':1, 'image':str(profile.profile_picture) if profile.profile_picture else None}
            if cover_photos:
                preferences_by_user_id['cover_photos'] = [{'id':i, 'image':str(cover_photo.image)} for i,cover_photo in enumerate(cover_photos, start=1)]
                preferences_by_user_id['cover_photos'].insert(0, {'id':0, 'image':str(profile.profile_picture) if profile.profile_picture else None})
            else:
         
                preferences_by_user_id['cover_photos'] = [{'id':0, 'image':str(profile.profile_picture) if profile.profile_picture else None}]
           
           
            preferences_by_user_id['height'] = profile.height
            preferences_by_user_id['languages'] = [language.name for language in profile.languages.all()]
            favorite_status = True if Favorite.objects.filter(user=profile, favored_by=user_profile).first() else False
            like_status = True if Like.objects.filter(user=profile, liked_by=user_profile).first() else False
            preferences_by_user_id['favorite_status'] = favorite_status
            preferences_by_user_id['like_status'] = like_status
            preferences_by_user_id['distance'] = haversine_distance(user_profile.latitude, user_profile.longitude, profile.latitude, profile.longitude) if profile.user.showDistance else False
            for field_name, choice_queryset in field_mapping.items():
                if choice_queryset.all():
                    for choice in choice_queryset.all():
                        profile_value = str(getattr(profile, field_name))
                        if profile_value == str(choice):
                            matches_count += 1
                            preferences_by_user_id[field_name] = profile_value
            print(f"choice count:{choice_count} matches count:{matches_count}")
            preferences_by_user_id['match_percentage'] = (matches_count / choice_count) * 100        
            match_percentage = (matches_count / choice_count) * 100
            print(f"match percentage:{match_percentage}")
            # if match_percentage == 100 or match_percentage == 0:
            
            preferences_list.append(preferences_by_user_id)
        
        # Return the list of preferences
        return Response({'preferences_by_user_id': preferences_list}, status=status.HTTP_200_OK)

def get_package_expired(obj):
    package_validity = obj.user.package_validity
    if not package_validity:
        return True
    current_date = timezone.now()
    return current_date > package_validity

GENDER_CHOICES = {
'M':'Male',
'F':'Female',
'TM':'Transgender Male',
'TF':'Transgender Female',
}
ORIENTATION_CHOICES = {
    'Hetero':'Heterosexual',
    'Homo':'Homo',
    'Pan':'Pansexual',
    'Bi':'Bisexual',
}
class getUserProfilesForAdmin(GenericAPIView):
    
    @swagger_auto_schema(
        operation_summary="Get User Profiles for Admin",
        operation_description="Retrieve user profiles for admin based on specified criteria.",
        manual_parameters=[
            openapi.Parameter('type', in_=openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Type of device (web/mobile)', default='web'),
        ],
        responses={
            200: openapi.Response(
                'Successful response - Returns a list of user profiles for admin',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'interests': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                            'date_of_birth': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='User\'s date of birth'),
                            'age': openapi.Schema(type=openapi.TYPE_INTEGER, description='User\'s age'),
                            'profile_picture': openapi.Schema(type=openapi.TYPE_OBJECT, properties={'id': openapi.Schema(type=openapi.TYPE_INTEGER), 'image': openapi.Schema(type=openapi.TYPE_STRING)}),
                            'cover_photos': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'id': openapi.Schema(type=openapi.TYPE_INTEGER), 'image': openapi.Schema(type=openapi.TYPE_STRING)})),
                            'height': openapi.Schema(type=openapi.TYPE_STRING),
                            'languages': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                            'is_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            'membership_status': openapi.Schema(type=openapi.TYPE_STRING),
                            'date_joined': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Date the user joined'),
                            'distance': openapi.Schema(type=openapi.TYPE_NUMBER, description='Distance from the requesting user'),
                            'city': openapi.Schema(type=openapi.TYPE_STRING),
                            'country': openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
            401: "Unauthorized - User doesn't have privileges for this API",
        },
        tags=["Admin"],
    )
    def get(self, request):
        """
        Retrieve user profiles for admin based on specified criteria.
        """
              
        
        
        user = self.request.user
        user_profile = UserProfile.objects.get(user=user)
        
        device = request.headers.get('type', 'web')
        rowsPerPage = request.headers.get('rowsperpage',0)
        currentPage = request.headers.get('page',0)
        
        matching_profiles = UserProfile.objects.all().order_by("-created_at")
        total_count = matching_profiles.count()
        if rowsPerPage and currentPage: 
                    paginator = Paginator(matching_profiles, rowsPerPage)
                    
                    try:
                        matching_profiles = paginator.page(currentPage)
                    except EmptyPage:
                        return Response("Page not found", status=status.HTTP_404_NOT_FOUND)
                    except PageNotAnInteger:
                        return Response("Invalid page number", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Page Number and RowsPerPage should be pass in API", status=status.HTTP_500_INTERNAL_SERVER_ERROR)       

        # Create a list to store user preferences
        preferences_list = []
        current_date = datetime.now()
        for profile in matching_profiles:
            user_id = profile.user.id
            cover_photos = CoverPhoto.objects.filter(user_profile = profile)
            
            print(f"user_id:{user_id}")
            matches_count = 0
            preferences_by_user_id = {}
            preferences_by_user_id['id'] = profile.user.id
            preferences_by_user_id['username'] = profile.user.username
            preferences_by_user_id['email'] = profile.user.email
            if device == 'mobile':
                preferences_by_user_id['interests'] = [{'id':interests.id, 'name':interests.name }for interests in profile.user.interests.all()]
            else:    
                preferences_by_user_id['interests'] = [interests.name for interests in profile.user.interests.all()]
            if profile.user.date_of_birth:
                preferences_by_user_id['date_of_birth'] = profile.user.date_of_birth
                age = current_date.year - profile.user.date_of_birth.year - ((current_date.month, current_date.day) < (profile.user.date_of_birth.month, profile.user.date_of_birth.day)) 
                preferences_by_user_id['age'] = age if profile.user.showAge else False
            preferences_by_user_id['profile_picture'] = {
                'id':1, 'image':str(profile.profile_picture) if profile.profile_picture else None}
            if cover_photos:
                preferences_by_user_id['cover_photos'] = [{'id':i, 'image':str(cover_photo.image)} for i,cover_photo in enumerate(cover_photos, start=1)]
                preferences_by_user_id['cover_photos'].insert(0, {'id':0, 'image':str(profile.profile_picture) if profile.profile_picture else None})
            else:
         
                preferences_by_user_id['cover_photos'] = [{'id':0, 'image':str(profile.profile_picture) if profile.profile_picture else None}]
           
            preferences_by_user_id['gender'] = GENDER_CHOICES.get(profile.user.gender, None)
            preferences_by_user_id['orientation'] = ORIENTATION_CHOICES.get(profile.user.orientation,None)
            preferences_by_user_id['height'] = profile.height
            preferences_by_user_id['languages'] = [language.name for language in profile.languages.all()]
            preferences_by_user_id['is_verified'] = profile.user.is_verified
            preferences_by_user_id['membership_status'] = get_package_expired(profile)
            preferences_by_user_id['date_joined'] = profile.user.date_joined
            preferences_by_user_id['distance'] = haversine_distance(user_profile.latitude, user_profile.longitude, profile.latitude, profile.longitude) if profile.user.showDistance else False
            preferences_by_user_id['city'] = profile.city
            preferences_by_user_id['country'] = profile.country
            
            
      
            # if match_percentage == 100 or match_percentage == 0:
            
            preferences_list.append(preferences_by_user_id)
        
        # Return the list of preferences
        return Response({'users':preferences_list,
                         'users_count':total_count,
                         }, status=status.HTTP_200_OK)

class Enable2FA(GenericAPIView):
    
    @swagger_auto_schema(
        responses={
            200: "2FA Enabled Successfully",
        },
    )
    def patch(self, request):
        action = 'Enabled'
        user = User.objects.get(id = self.request.user.id)
        if user.has_2fa_enabled == True:
             user.has_2fa_enabled = False
             action = 'Disabled'
        else:
            user.has_2fa_enabled = True
        user.save()
        return Response({"status":True, "message":f"{action} 2FF for user {self.request.user}"}, status=status.HTTP_200_OK)
    
def add_notification(from_user, to_user, type, description ):

    notification = Notification.objects.create(from_user = from_user, to_user = to_user,
                                               type = type, description = description)
    notification.save()
def remove_notification(from_user, to_user, type):
    try:
        notification = Notification.objects.filter(from_user=from_user, to_user=to_user, type=type).first()
        if notification:
            notification.delete()
    except Notification.DoesNotExist:
        # Handle the case when the notification does not exist
        print(f"Notification not found")


class UserNotifications(GenericAPIView):

    @swagger_auto_schema(
        operation_summary="List Notifications",
        operation_description="List all notifications for the current user.",
        tags=["Notification"],
        responses={200: NotificationSerializer(many=True), 400: "Error message if any"},
    )
    def get(self, request):
        user_profile = UserProfile.objects.get(user=self.request.user)
        notifications = Notification.objects.filter(to_user=user_profile)
        unseen_notifications_count = Notification.objects.filter(to_user=user_profile, user_has_seen=False).count()

        # Serialize the notifications using your custom serializer
        serializer = NotificationSerializer(notifications, many=True)
        serializer_data = serializer.data

        response_data = {
            'status': True,
            'notifications': serializer_data,
            'unseen_notifications_count': unseen_notifications_count,
            'seen_status': True if not unseen_notifications_count else False
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Mark Notifications as Seen",
        operation_description="Mark all unread notifications as seen for the current user.",
        responses={200: "Notifications marked as seen successfully", 400: "Error message if any"},
        tags=["Notification"],
    )
    def patch(self, request):
        try:
            user_profile = UserProfile.objects.get(user=self.request.user)
            notifications = Notification.objects.filter(to_user=user_profile, user_has_seen=False)
            notifications.update(user_has_seen=True)

            return Response({'status': True, 'seen_status':True,'message': 'User Seen Notification Successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Clear Notifications",
        operation_description="Clear all notifications for the current user.",
        responses={200: "Notifications cleared successfully", 400: "Error message if any"},
        tags=["Notification"],
    )
    def delete(self, request):
        try:
            user_profile = UserProfile.objects.get(user=self.request.user)
            notifications = Notification.objects.filter(to_user=user_profile)
            notifications.delete()

            return Response({'status': True, '':'seen_status', 'message': 'Notifications cleared successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class GetClientId(GenericAPIView):
    def get(self, request):
        PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
        return Response(PAYPAL_CLIENT_ID, status=status.HTTP_200_OK)
    
class PackageListView(GenericAPIView):

    serializer_class = PackageSerializer

    def get_queryset(self):
        """
        Get the queryset for retrieving packages.
        """
        return Package.objects.all()

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description='Successful package list retrieval', schema=PackageSerializer(many=True)),
            500: openapi.Response(description='Internal Server Error'),
        },
        operation_summary="Retrieve Packages",
        operation_description="Retrieve a list of packages.",
        tags=["Package"],
    )
    def get(self, request):
        """
        Retrieve a list of packages.
        """
        try:
            # Retrieve the list of packages
            packages = Package.objects.all()
            package_list = []
            for package in packages:
                package_dict = {
                    'id':package.id,
                    'name':package.name,
                    'package_img':str(package.package_img),
                    'features':json.loads(package.features.replace("'", '"')) if package.features else None,
                    'price':package.price,
                    'type':package.type,
                    'validity':package.validity,
                }
                package_list.append(package_dict)
            return Response(package_list, status=status.HTTP_200_OK)


        except Exception as e:
            # Log the exception or handle it as needed
            # You might want to customize this based on your application's needs
            return Response({'detail': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    

    @swagger_auto_schema(
        request_body=PackageSerializer,
        responses={
            200: openapi.Response(description='Successfully created instance', schema=PackageSerializer(many=True)),
            400: openapi.Response(description='Bad Request - Invalid data provided'),
            500: openapi.Response(description='Internal Server Error'),
        },
        operation_summary="Create new package",
        operation_description="Create new package.",
        tags=["Package"],
    )
    def post(self, request):
        """
        Create a new instance of YourModel.
        """
        try:
            # Validate and save the serializer data
            serializer = self.serializer_class(data=request.data, partial=False)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log the exception or handle it as needed
            # You might want to customize this based on your application's needs
            return Response({'detail': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

  
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Package ID'),
                # Include other properties from PackageSerializer if needed
            },
            required=['id'],
        ),
        responses={
            200: openapi.Response(description='Successfully updated package instance', schema=PackageSerializer),
            400: openapi.Response(description='Bad Request - Invalid data provided'),
            404: openapi.Response(description='Not Found - Package not found'),
            500: openapi.Response(description='Internal Server Error'),
        },
        operation_summary="Update Package",
        operation_description="Update an existing Package instance.",
        tags=["Package"],
    )
    def put(self, request):
        """
        Update an existing Package instance.
        """
        try:
            # Extract package_id from request data
            package_id = request.data.get('id', None)
            
            # Check if package_id is provided
            if not package_id:
                return Response({"id": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
            
            # Retrieve the package instance
            package_instance = Package.objects.get(id=package_id)
        except Package.DoesNotExist:
            return Response({"detail": "Package not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validate and save the serializer data
        serializer = self.serializer_class(instance=package_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Package ID'),
            },
            required=['id'],
        ),
        responses={
            200: openapi.Response(description='Successfully deleted package instance'),
            400: openapi.Response(description='Bad Request - Invalid data provided'),
            404: openapi.Response(description='Not Found - Package not found'),
            500: openapi.Response(description='Internal Server Error'),
        },
        operation_summary="Delete Package",
        operation_description="Delete an existing Package instance.",
        tags=["Package"],
    )
    def delete(self, request):
        """
        Delete an existing Package instance.
        """
        try:
            
            # Extract package_id from request data
            package_id = request.data.get('id', None)
            
            # Check if package_id is provided
            if not package_id:
                return Response({"id": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
            
            # Retrieve the package instance
            package_instance = Package.objects.get(id=package_id)
        except Package.DoesNotExist:
            return Response({"detail": "Package not found."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the package instance
        package_instance.delete()
        return Response({"detail": "Package Deleted Successfully"}, status=status.HTTP_200_OK)
    
    
class GetKycCategory(GenericAPIView): 
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="KYC categories retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='KYC category ID'),
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the KYC category'),
                        }
                    )
                )
            ),
            500: "Internal Server Error: An error occurred"
        },
        operation_summary="Get KYC categories",
        operation_description="This endpoint retrieves all KYC categories.",
        tags=["KYC Categories"],
    )
    def get(self, request):
        categories = KycCategory.objects.all()
        category_list = []
        for category in categories:
            category_dict = {
                'id':category.id,
                'name':category.name
            }
            category_list.append(category_dict)
        return Response(category_list, status=status.HTTP_200_OK)
    
class UploadKYC(GenericAPIView):
    
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'document': openapi.Schema(type=openapi.TYPE_STRING, description='Base64 encoded document image'),
            'type': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the KYC category'),
        },
        required=['document', 'type'],
    ),
        responses={
            201: openapi.Response(
                description="KYC document created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='KYC document ID'),
                        'document': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the KYC document image'),
                        'type': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the KYC category'),
                    }
                )
            ),
            400: "Bad Request: Missing required fields or invalid data",
            401: "Unauthorized: User authentication failed",
            404: "Not Found: KYC category not found",
            500: "Internal Server Error: An error occurred"
        },
        operation_summary="Create a new KYC document",
        operation_description="This endpoint allows the authenticated user to create a new KYC document.",
        tags=["KYC Documents"],
    )

    def post(self, request):
        # Get the authenticated user
        # user = User.objects.get(username=request.user)

        
        # Get the user's profile
        user_profile = UserProfile.objects.get(user__username=request.user)

        # Extract required data from the request
        
        document = request.data.get('document')
        type_id = request.data.get('type')
        
        # Get the KYC category based on the provided type ID
        try:
            category_type = KycCategory.objects.get(id=type_id)
        except KycCategory.DoesNotExist:
            return Response("Invalid KYC category ID", status=status.HTTP_404_NOT_FOUND)

        try:
            kycDoc = KycDocument.objects.get(user_profile = user_profile, type = category_type, status = 0)
            if kycDoc:
                return Response(f'{category_type} Kyc document already uploaded and its in pending state', status=status.HTTP_400_BAD_REQUEST)
        except KycDocument.DoesNotExist:
            pass
        # Create a new KYC document instance
        KycDocument.objects.create(
            user_profile=user_profile,
            document=document,
            type=category_type,
        )

        return Response("KYC uploaded successfully", status=status.HTTP_200_OK)
    @swagger_auto_schema(
    responses={
        200: openapi.Response(
            description="KYC documents retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='KYC document ID'),
                        'image': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the KYC document image'),
                    }
                )
            )
        ),
        401: "Unauthorized: User authentication failed",
        404: "Not Found: User profile or KYC documents not found",
        500: "Internal Server Error: An error occurred"
    },
    operation_summary="Get KYC documents for the authenticated user",
    operation_description="This endpoint retrieves KYC documents associated with the authenticated user's profile.",
    tags=["KYC Documents"],
)
    def get(self, request):
        
        isAdmin = False
        
        loginUser = User.objects.get(username = request.user)
        username = request.headers.get('username', 0)
        device = request.headers.get('device','web')
        # request.headers.get('username')
        type = int(request.headers.get('status'))
        print(f"TYPE:{type}, USERNAME:{username}")
        if username:
                user_profile = UserProfile.objects.get(user__username=username)
        if loginUser.is_admin:
            isAdmin = True
              # Retrieve KYC documents for the user's profile
            if username:
                if type != 4:
                    documents = KycDocument.objects.filter(user_profile=user_profile, status = type).all()
                else:
                    documents = KycDocument .objects.filter(user_profile=user_profile).all()
            else: 
                if type !=4:
                    documents = KycDocument.objects.filter(status = type).all()
                    print(f"HEREEEE")
                else:
                    documents = KycDocument.objects.all()
                
         
            
        
        else:
            
            # Get the user's profile
            user_profile = UserProfile.objects.get(user__username=loginUser)
            documents = KycDocument .objects.filter(user_profile=user_profile).all()
        kyc_count = documents.count()
      
        
        if isAdmin and device == 'web':
            
            rowsPerPage = request.headers.get('rowsperpage',5)
            currentPage = request.headers.get('page',1)
              # Paginate the queryset
            paginator = Paginator(documents, rowsPerPage)
            
            try:
                documents = paginator.page(currentPage)
            except EmptyPage:
                return Response("Page not found", status=status.HTTP_404_NOT_FOUND)
            except PageNotAnInteger:
                return Response("Invalid page number", status=status.HTTP_400_BAD_REQUEST)
            
            
        kyc_list = []  
        print(f"DOCUMENTS:{documents}")
        print(f"isAdmin:{isAdmin}")
        if not documents:
             return Response(kyc_list, status=status.HTTP_200_OK)
        # Prepare a list of dictionaries containing KYC document details
        status_codes ={'0':'Pending',
                        '1':'Approved',
                        '2':'Rejected'}
        for document in documents:
            live_mode = settings.LIVE_MODE
            image_path = str(document.document.url).replace("/media",'') if document.document else None if not live_mode else  str(document.document.url).replace("/djangoapi/media",'') if document.document else None
            kyc_dict = {
                'id': document.id,
                'username':document.user_profile.user.username,
                'image': image_path,
                'type':document.type.name,
                'status': status_codes.get(str(document.status), None),
                'isAdmin':isAdmin,
            }
            kyc_list.append(kyc_dict)
        if isAdmin:
            return Response({'kyc_list':kyc_list,
                            'kyc_count':kyc_count
                            }, status=status.HTTP_200_OK)
        else:
            return Response(kyc_list, status=status.HTTP_200_OK)
            
    

    
    @swagger_auto_schema(
    operation_summary="Update KYC document status",
    operation_description="This endpoint allows an admin user to update the status of KYC documents.",
    manual_parameters=[
        openapi.Parameter('kyc_ids', in_=openapi.IN_HEADER, description="List of KYC IDs", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), required=True),
        openapi.Parameter('status', in_=openapi.IN_HEADER, description="New status for KYC documents", type=openapi.TYPE_STRING, required=True, enum=["0:Pending", "1:Approved", "2:Rejected"]),
    ],
    responses={
        200: "KYC document status updated successfully",
        401: "Unauthorized: You don't have the privilege to edit the KYC document",
        400: "Bad Request: Both 'kyc_id' and 'status' are required in the request data.",
        404: "Not Found: User not found or KYC document not found",
        500: "Internal Server Error: An error occurred"
    },
 
    tags=["KYC Documents"],
    )
    def patch(self, request):
        try:
            # Get the authenticated user
            user = User.objects.get(username=request.user)
            
            # Check if the user is an admin
            if not user.is_admin:
                return Response("You don't have the privilege to edit the KYC document", status=status.HTTP_401_UNAUTHORIZED)
            
            # Extract data from the request
            kyc_ids = request.data.get('kyc_ids', [])
            status_value = request.data.get('status')
            print(f"kyc_ids:{kyc_ids}")
            # Check if both 'kyc_id' and 'status' are provided in the request data
            if not kyc_ids or not status_value:
                raise ParseError("Both 'kyc_id' and 'status' are required in the request data.")
            
            # Retrieve the KYC document using the provided 'kyc_id'
            kyc_doc = KycDocument.objects.filter(id__in=kyc_ids)
            
            user_ids = [kycDoc.user_profile.user.id for kycDoc in kyc_doc]
            # Update the status of the KYC document
            kyc_doc.update(status =  status_value) 
            
            if status_value == 1:
                users = User.objects.filter(id__in = user_ids)
                users.update(is_verified = True)

            
            return Response("KYC document status updated successfully", status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            # If the user is not found, return a 404 response
            raise NotFound("User not found")
        
        except KycDocument.DoesNotExist:
            # If the KYC document is not found, return a 404 response
            raise NotFound("KYC document not found")
        
        except Exception as e:
            # Handle other exceptions and return a 500 response with the error message
            return Response(f"An error occurred: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'kyc_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the KYC document to be deleted'),
        },
        required=['kyc_id'],
    ),
    responses={
        204: "KYC document deleted successfully",
        400: "Bad Request: Missing required fields or invalid data",
        401: "Unauthorized: User authentication failed",
        404: "Not Found: User, user profile, or KYC document not found",
        500: "Internal Server Error: An error occurred"
    },
    operation_summary="Delete a KYC document",
    operation_description="This endpoint allows the authenticated user to delete a KYC document.",
    tags=["KYC Documents"],
)
    def delete(self, request):
        try:
            # Get the authenticated user
            user = User.objects.get(username=request.user)

            # Get the user's profile
            user_profile = UserProfile.objects.get(user=user)

            # Extract 'kyc_id' from the request data
            kyc_id = request.data.get('kyc_id')
            
            # Check if 'kyc_id' is provided in the request data
            if not kyc_id:
                raise ParseError("'kyc_id' is required in the request data.")

            # Retrieve the KYC document using the provided 'kyc_id' and user profile
            kyc_doc = KycDocument.objects.filter(id=kyc_id, user_profile=user_profile).first()

            # Check if the KYC document exists
            if not kyc_doc:
                return Response("Not Found: KYC document not found", status=status.HTTP_404_NOT_FOUND)

            # Delete the KYC document
            kyc_doc.delete()

            return Response("KYC document deleted successfully", status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response("Not Found: User not found", status=status.HTTP_404_NOT_FOUND)

        except UserProfile.DoesNotExist:
            return Response("Not Found: User profile not found", status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response(f"Internal Server Error: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class MlmRegister(GenericAPIView):
    
    @swagger_auto_schema(
        operation_summary="MLM User Registration",
        operation_description="Register a new user in the MLM system.",
        responses={200: "Registration successful", 400: "Error message if any"},
        tags=["MLM"],
    )
    def post(self, request):
        try:
            # Get the authenticated user
            # sponsor_name = self.kwargs.get('sponsor_name')
            
            # 'Sagalovskiy'
            user = User.objects.get(username=request.user)
            sponsor_id = str(user.sponsor.id) if  user.sponsor else '1'

            print(f"sponsor_id:{sponsor_id}")
            # MLM API endpoint URL
            url = f'{settings.MLM_ADMIN_URL}/api/register'

            # Prepare data for the POST request
            data = {
                '_token': settings.MLM_API_KEY,
                'username': user.username,
                'user_ref_id':user.id,
                'sponsor_id': sponsor_id,
                'first_name': user.username,
                'date_of_birth': user.date_of_birth,
                'gender': user.gender,
                'email': user.email,
                'mobile': user.phone_number,
                'password': 12345678,  # Note: Sending the password in plaintext is not recommended
                'totalAmount': '100'
            }

            # Make a POST request
            response = requests.post(url, data=data)

            # Check the response status
            if response.status_code == 200:
                print('POST request successful!')
                print('Response:', response.text)
                return Response(response.text, status=status.HTTP_200_OK)
            else:
                print(f'Error: {response.status_code}')
                print('Response:', response.text)
                return Response(response.text, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            # Handle the case where the user is not found
            print('Error: User not found')
            return Response('User not found', status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Handle other unexpected exceptions
            print(f'Error: {str(e)}')
            return Response('Internal Server Error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ContactUsMail(GenericAPIView):
    @swagger_auto_schema(
        operation_summary="Send Support Email",
        operation_description="Send a support email based on the provided data.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Sender\'s email address'),
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Message content'),
            },
            required=['email', 'message'],
        ),
        responses={
            200: "Email sent successfully",
            400: "Bad Request - Missing required fields or invalid data",
            500: "Internal Server Error - An error occurred during email sending",
        },
        tags=["ContactUs"],
    )
    def post(self, request):
        """
        Send a support email based on the provided data.

        Expected input in the request data:
        - email: The sender's email address
        - message: The message content

        Returns a response indicating the success or failure of the email sending process.
        """
        try:
            # Extract data from the request
            email = request.data.get('email')
            message = request.data.get('message')

            # Validate that email and message are provided
            if not email or not message:
                raise ValueError("Both 'email' and 'message' are required fields.")

            # Set the sender's email address
            email_from = settings.DEFAULT_FROM_EMAIL
            # Send the email
            threading.Thread(target=send_mail, args=('Support', message, email_from, [email])).start()
            # send_mail('Support', message, email_from, [email])

            # Optionally, you can return a success response
            return Response({'detail': 'Email sent successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception or handle it as needed
            # You might want to customize this based on your application's needs
            return Response({'detail': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        
        
        
  
        
class MailContent(GenericAPIView):
    permission_classes = [IsAuthenticated]  # Require authentication for this view
    @swagger_auto_schema(
        operation_summary="Retrieve Mail Content",
        operation_description="Retrieve mail content based on the specified type.",
        manual_parameters=[
            openapi.Parameter('type', in_=openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Type of mail', example='reset_password, otp(Your account verification email), register'),
        ],
        responses={
            200: openapi.Response(
                'Successful response - Returns mail content',
            ),
            400: "Bad Request - Missing or invalid 'type' header",
            401: "Unauthorized - User doesn't have privileges for this API",
            404: "Not Found - User or mail content not found",
        },
        tags=["MailContent"],
    )
    def get(self, request):
        """
        Retrieve mail content based on the specified type.
        """
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            mail_type = request.headers['type']
        except KeyError as e:
            return Response(f"{str(e)} Required", status= status.HTTP_400_BAD_REQUEST)

        if not user.is_admin:
            return Response("User doesn't have privileges for this API", status=status.HTTP_401_UNAUTHORIZED)

        try:
            mail_content = EmailTemplate.objects.get(type=mail_type)
        except EmailTemplate.DoesNotExist:
            return Response({"detail": "Mail content not found"}, status=status.HTTP_404_NOT_FOUND)

        # Return a simple JSON response without serialization
        return Response({
            "type": mail_content.type,
            "subject": mail_content.subject,
            "content": mail_content.content,
            # Include other fields as needed
        }, status=status.HTTP_200_OK) 
        
        
    @swagger_auto_schema(
        operation_summary="Update Mail Content",
        operation_description="Update mail content based on the specified type.",
        # manual_parameters=[
        #     openapi.Parameter('type', in_=openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Type of mail', example='register, otp, reset_password'),
        # ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'subject': openapi.Schema(type=openapi.TYPE_STRING, description='New subject for the mail'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='New content for the mail'),
                'type': openapi.Schema(type=openapi.TYPE_STRING, description='register, otp, reset_password'),
            },
            required=['subject', 'content'],
        ),
        responses={
            200: openapi.Response(
                'Successful response - Returns updated mail content',
            ),
            400: "Bad Request - Missing required fields or invalid data",
            401: "Unauthorized - User doesn't have privileges for this API",
            404: "Not Found - User or mail content not found",
        },
        tags=["MailContent"],
    )
    def put(self, request):
        """
        Update mail content based on the specified type.
        """
        try:
            mail_type = request.data['type']
            user = User.objects.get(id=request.user.id)
            if not user.is_admin:
                return Response("User doesn't have privileges for this API", status=status.HTTP_401_UNAUTHORIZED)

            mail_content = EmailTemplate.objects.get(type=mail_type)
            mail_content.subject =  request.data.get('subject', mail_content.subject)
            mail_content.content = request.data.get('content',mail_content.content)

            mail_content.save()
            
            
            
            # Return a simple JSON response without serialization
            return Response({
                "type": mail_content.type,
                "subject": mail_content.subject,
                "content": mail_content.content,
                # Include other fields as needed
            }, status=status.HTTP_200_OK) 
            
            
        except EmailTemplate.DoesNotExist:
            return Response({"detail": "Mail content not found"}, status=status.HTTP_404_NOT_FOUND)
            
            
        except KeyError as e:
            return Response(f"{str(e)} Required", status= status.HTTP_400_BAD_REQUEST)
        
class CompanyDetails(GenericAPIView):
    
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({'Company Name':'Dating',
                         'Location':'USA',
                         'Email':'dating@hotmail.com'},
                        status=status.HTTP_200_OK)
        
class AdminConfigurations(APIView):
    
    
    @swagger_auto_schema(
        operation_summary="Update Mail Content",
        operation_description="Update mail content based on the specified type.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'company_name': openapi.Schema(type=openapi.TYPE_STRING, description='New company name'),
                'company_mail': openapi.Schema(type=openapi.TYPE_STRING, description='New company mail'),
                'company_address':openapi.Schema(type=openapi.TYPE_STRING, description='New company address'),
                'email_host': openapi.Schema(type=openapi.TYPE_STRING, description='New email host'),
                'email_port': openapi.Schema(type=openapi.TYPE_INTEGER, description='New email port'),
                'email_host_user': openapi.Schema(type=openapi.TYPE_STRING, description='New email host user'),
                'email_host_password': openapi.Schema(type=openapi.TYPE_STRING, description='New email host password'),
                'email_tls': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='New email TLS'),
                'paypal_client_id': openapi.Schema(type=openapi.TYPE_STRING, description='New PayPal client ID'),
                'paypal_client_secret': openapi.Schema(type=openapi.TYPE_STRING, description='New PayPal client secret'),
                'paypal_base_url': openapi.Schema(type=openapi.TYPE_STRING, description='New PayPal base URL'),
            },
            required=['company_name', 'company_mail', 'email_host', 'email_port', 'email_host_user', 'email_host_password', 'email_tls', 'paypal_client_id', 'paypal_client_secret', 'paypal_base_url'],
        ),
        responses={
            200: openapi.Response(
                'Successful response - Returns updated configuration',
                schema=ConfigurationSerializer,
            ),
            400: "Bad Request - Missing required fields or invalid data",
        },
        tags=["Admin"],
    )
    def post(self, request, *args, **kwargs):
        
        
        user = User.objects.get(username = request.user)
        if not user.is_admin:
            return Response(f"{request.user} Don't have privillages to this API")
        
        serializer = ConfigurationSerializer(data=request.data, partial=True)
        
        configurations = Configurations.objects.first()
        if configurations:
            serializer =ConfigurationSerializer(configurations, data=request.data)
        else:
            serializer = ConfigurationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Retrieve Mail Content",
        operation_description="Retrieve mail content if available.",
        responses={
            200: openapi.Response(
                'Successful response - Returns configuration data',
                schema=ConfigurationSerializer,
            ),
            404: "Not Found - Configuration not found",
        },
        tags=["Admin"],
    )
    def get(self, request, *args, **kwargs):
        configurations = Configurations.objects.first()
        user = User.objects.get(username = request.user)
        if not user.is_admin:
            return Response(f"{request.user} Don't have privillages to this API")
        
        if configurations:
            serializer = ConfigurationSerializer(configurations)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(f"Detail:Configuration not found", status=status.HTTP_404_NOT_FOUND)
        
class CompanyDetails(APIView):
    
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'privacy_policy': openapi.Schema(type=openapi.TYPE_STRING, description='Privacy policy text'),
                'terms_and_conditions': openapi.Schema(type=openapi.TYPE_STRING, description='Terms and conditions text'),
            },
            required=['privacy_policy', 'terms_and_conditions'],
        ),
        responses={
            200: openapi.Response(
                'Successful response - Returns serialized company data',
                schema=CompanyDataSerializer,
            ),
            500: "Internal Server Error - Failed to process the request",
        },
        operation_summary="Create or update company data",
        operation_description="This API allows creating or updating company data with privacy policy and terms and conditions.",
        tags=["Admin"],
    )
    def post(self, request, *args, **kwargs):
        
        company_data = CompanyData.objects.first()
        
        if not company_data:
            company_serializer = CompanyDataSerializer(data = request.data, partial = True)
        else:
            company_serializer = CompanyDataSerializer(company_data, data = request.data)
            
        if company_serializer.is_valid():
            company_serializer.save()
            return Response(company_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(company_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                'Successful response - Returns serialized company data',
                schema=CompanyDataSerializer,
            ),
            404: "Not Found - Company details not found",
        },
        operation_summary="Retrieve company data",
        operation_description="This API retrieves the company data, including privacy policy and terms and conditions.",
        tags=["Admin"],
    )    
    def get(self, request):
        
        companyData = CompanyData.objects.first()
        if companyData:
            company_serializer = CompanyDataSerializer(companyData)
            return Response(company_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(f"Company Details not found", status=status.HTTP_404_NOT_FOUND)