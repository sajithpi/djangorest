from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from . models import User, UserProfile, CoverPhoto, Interest, EducationType, RelationShipGoal, Religion, FamilyPlanChoice, DrinkChoice, Workout, Language, SmokeChoice, ProfilePreference, Notification
from . serializers import UserSerializers, UpdateUserSerializer, UpdateUserProfileSerializer, CoverPhotoSerializer, UserProfileSerializer, ProfilePreferenceSerializerForMobile, InterestSerializer, CombinedSerializer, ProfilePreferenceSerializer, NotificationSerializer
from rest_framework import status, permissions
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from rest_framework.serializers import Serializer
from datetime import datetime
from user_agents import parse
from django.core import serializers
from django.conf import settings
import json
from django.http import QueryDict
from followers.models import Favorite, Like, BlockedUser, Rating
from html import escape
import math

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
    permission_classes = (IsAuthenticated,TwoFactorAuthRequired)
    
    @swagger_auto_schema(
    operation_description="Get user data",  # Describe the operation
    responses={200: UserProfileSerializer},  # Define the response schema
    tags=["User"],  # Categorize the endpoint using tags
    )
    def get(self, request):

        user_agent_string = request.META.get('HTTP_USER_AGENT')
        user_agent = parse(user_agent_string)

        user = self.request.user
        print(f"user agent details:{user_agent}")
        device = user_agent.device
        print(f"device:{device}")
        client_ip = request.META.get('REMOTE_ADDR')
        print(f"my ip:{client_ip}")

        print(f"browser:{user_agent.browser.family}")
        device = request.headers.get('device','web')
        # device = request.headers['device'] if request.headers['device'] else 'web'
        print(f"device:{device}")
         #get the user's profile 
        profile = UserProfile.objects.get(user=user)
        
                # Fetch user interests
        interests = profile.user.interests.all()
        
        # Serialize profile data with interests
        profile_serializer = UserProfileSerializer(profile, context = {'device':device})
        
        
        data = profile_serializer.data
        print(f"data:{data}")
          # Add interests to the serialized data
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
                height = request.data.get('height')
                print(f"height type:{type(height)}")
                print(f"height:{height}")
                if height:
                    feet = height[0]['feet']
                    print(f"feet:{feet}")
                    inches = height[0]['inches']
                    cm = height[0]['cm']
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
                    
                if request.data['height'] < 0:
                    return Response({f'status':'error','message':'Height cannot be less than 0'},status=status.HTTP_400_BAD_REQUEST)
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


            # interest_name = request.data.get('interests',None)
            # if interest_name:
            #     interest_name = interest_name.strip('"')
            #     print(f"interest name:{interest_name}")
            #     interest= Interest.objects.get(name=interest_name)
            #     user.interests.add(interest)
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
  
class UpdateUserLocation(GenericAPIView):
    permission_classes = (IsAuthenticated,TwoFactorAuthRequired)

    def post(self, request):
        try:
            user = User.objects.get(username=self.request.user)
            user_profile = UserProfile.objects.get(user=user)
            if self.request.data.get('longitude') and self.request.data.get('latitude'):
                user_profile.longitude = self.request.data.get('longitude')
                user_profile.latitude = self.request.data.get('latitude')
                user_profile.city = self.request.data.get('city','city')
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
            profile_data = {
                'id':data['user']['id'],
                'username':data['user']['username'],
                'about_me':lorem_ipsum,
                'age':calculate_age(datetime.strptime(data['user']['date_of_birth'], '%Y-%m-%d')),
                'profile_picture':data['profile_picture'],
                'distance': haversine_distance(current_user_profile.latitude, current_user_profile.longitude, profile.latitude, profile.longitude),
                'interests':data['interests'],
                'rating_users':rating_users if rating_users else [],
                'cover_photos':data['cover_photos'],
                'favorite_status':favorite_status,
                'like_status':like_status,
                'block_status':block_status,
                          
            }
            
            return Response(profile_data, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

class GetMyPreferences(GenericAPIView):
    @swagger_auto_schema(
        operation_description="Get user preferences",  # Describe the operation
        responses={200: ProfilePreferenceSerializer()},  # Define the response schema
        tags=["User"],  # Categorize the endpoint using tags
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
        tags=["User"],
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
        tags=["User"],
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
            openapi.Parameter('email', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Email address to check")
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
        }
    )
    def post(self, request):
        email = request.data.get('email', None)
        
        if not email:
            return Response({'message':'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'message':'User with this email already exists'}, status=status.HTTP_200_OK)
        else:
            return Response({'message':'User with this email not exists'}, status=status.HTTP_200_OK)
        
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
        }
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
    tags=["User"],  # Categorize the endpoint using tags
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
            languages_data = [{'label': language.name, 'value': language.name} for language in languages]
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
    )
    def get(self, request):
        # Retrieve the user's preferences
        user = self.request.user
        user_profile = UserProfile.objects.get(user=user)
        user_gender = user_profile.user.gender
        user_orientation = user_profile.user.orientation
    

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
            combined_filter |= q_obj
        # Create a Q object to represent the exclusion condition
        exclude_blocked_users = Q(user__id__in=blocked_users)

        # Query to find matching user profiles
        matching_profiles = UserProfile.objects.filter(
            combined_filter & ~exclude_blocked_users,
            user__gender=user_partner_gender_preference,
            user__orientation=user_orientation
                )
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
            preferences_by_user_id['date_of_birth'] = profile.user.date_of_birth
            age = current_date.year - profile.user.date_of_birth.year - ((current_date.month, current_date.day) < (profile.user.date_of_birth.month, profile.user.date_of_birth.day)) 
            preferences_by_user_id['age'] = age
            preferences_by_user_id['profile_picture'] = {
                'id':1, 'image':str(profile.profile_picture) if profile.profile_picture else None}
            if cover_photos:
                preferences_by_user_id['cover_photos'] = [{'id':i, 'image':str(cover_photo.image)} for i,cover_photo in enumerate(cover_photos, start=1)]
            else:
                preferences_by_user_id['cover_photos'] = []
            preferences_by_user_id['height'] = profile.height
            preferences_by_user_id['languages'] = [language.name for language in profile.languages.all()]
            favorite_status = True if Favorite.objects.filter(user=profile, favored_by=user_profile).first() else False
            like_status = True if Like.objects.filter(user=profile, liked_by=user_profile).first() else False
            preferences_by_user_id['favorite_status'] = favorite_status
            preferences_by_user_id['like_status'] = like_status
            preferences_by_user_id['distance'] = haversine_distance(user_profile.latitude, user_profile.longitude, profile.latitude, profile.longitude)
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
            
            preferences_list.append(preferences_by_user_id)
        
        # Return the list of preferences
        return Response({'preferences_by_user_id': preferences_list}, status=status.HTTP_200_OK)


class Enable2FA(GenericAPIView):
    
    @swagger_auto_schema(
        responses={
            200: "2FA Enabled Successfully",
        },
    )
    def post(self, request):
        
        user = User.objects.get(id = self.request.user.id)
        user.has_2fa_enabled = True
        user.save()
        return Response(f"Enabled 2FF for user {self.request.user}", status=status.HTTP_200_OK)
    
def add_notification(from_user, to_user, type, description ):

    notification = Notification.objects.create(from_user = from_user, to_user = to_user,
                                               type = type, description = description)
    notification.save()
def remove_notification(from_user, to_user, type):
    try:
        notification = Notification.objects.get(from_user=from_user, to_user=to_user, type=type)
        notification.delete()
    except Notification.DoesNotExist:
        # Handle the case when the notification does not exist
        print(f"Notification not found")

class GetNotifications(GenericAPIView):

    def get(self, request):
        user_profile = UserProfile.objects.get(user = self.request.user)
        notifications = Notification.objects.filter(to_user = user_profile)
        notifications .update(user_has_seen = True)
        
        # Serialize the notifications using your custom serializer
        serializer = NotificationSerializer(notifications, many = True)
        serializer_data = serializer.data

        return Response({'status':True, 'notifications':serializer_data}, status=status.HTTP_200_OK)