from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from . models import User, UserProfile, CoverPhoto, Interest, EducationType, RelationShipGoal, Religion, FamilyPlanChoice, DrinkChoice, Workout, Language, SmokeChoice, ProfilePreference
from . serializers import UserSerializers, UpdateUserSerializer, UpdateUserProfileSerializer, CoverPhotoSerializer, UserProfileSerializer, InterestSerializer, CombinedSerializer, ProfilePreferenceSerializer
from rest_framework import status, permissions
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from rest_framework.serializers import Serializer
from datetime import datetime
from user_agents import parse
from followers.models import Favorite, Like

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

         #get the user's profile 
        profile = UserProfile.objects.get(user=user)
        
                # Fetch user interests
        interests = profile.user.interests.all()
        
        # Serialize profile data with interests
        profile_serializer = UserProfileSerializer(profile)
        
        data = profile_serializer.data
        
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

            
            
        #Update fields in the User model if provided
        user_serializer = UpdateUserSerializer(user, data = request.data, partial = True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=400)
        
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
                
        except UserProfile.DoesNotExist:
            return Response({'error':'UserProfile does not exist for this user.'}, status=404)
        return Response({'message':'User Profile updated successfully'})
        # Return a success response
        return Response({'message': 'User information updated successfully'})
    
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
            interests_data = request.data.get('interest_id', [])
            print(f"interests_data:{interests_data}")
            user = User.objects.get(id=user_id)
            if interests_data:
                for interest_id in interests_data:
                    print(f"interest_id:{interest_id}")
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
    operation_description="Get user data",  # Describe the operation
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

        # Create dictionaries for each model's data
        interests_data = [{'id': interest.id, 'name': interest.name} for interest in interests]
        drink_choices_data = [{'id': choice.id, 'name': choice.name} for choice in drink_choices]
        family_plan_choices_data = [{'id': choice.id, 'name': choice.name} for choice in family_plan_choices]
        workouts_data = [{'id': workout.id, 'name': workout.name} for workout in workouts]
        religions_data = [{'id': religion.id, 'name': religion.name} for religion in religions]
        relationship_goals_data = [{'id': goal.id, 'name': goal.name} for goal in relationship_goals]
        smoke_choices_data = [{'id': choice.id, 'name': choice.name} for choice in smoke_choices]
        education_types_data = [{'id': education.id, 'name': education.name} for education in education_types]
        languages_data = [{'id': language.id, 'name': language.name} for language in languages]

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
            
            #Clear existing preferences
            profile_preference.family_choices.clear()
            profile_preference.drink_choices.clear()
            profile_preference.religion_choices.clear()
            profile_preference.education_choices.clear()
            profile_preference.relationship_choices.clear()
            profile_preference.workout_choices.clear()
            profile_preference.smoke_choices.clear()
            profile_preference.languages_choices.clear()
            
            serializer = ProfilePreferenceSerializer(profile_preference, data=request.data, partial =True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':"User Preference Updated Successfully", 'data':serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
class GetProfileMatches(GenericAPIView):
    @swagger_auto_schema(
        responses={
            200: "Success",
        },
    )
    def get(self, request):
        # Retrieve the user's preferences
        user = self.request.user
        user_profile = UserProfile.objects.get(user = user)
        user_gender = user_profile.user.gender
        user_orientation = user_profile.user.orientation
        print(f"USER {user} GENDER:{user_gender}, ORIENTATION:{user_orientation}")
        user_preferences = ProfilePreference.objects.get(user_profile = user_profile)
        print(f"user preferences:{user_preferences}")
        print(f"family preference:{user_preferences.family_choices.all()}")
        
        user_orientation_filter = {
            ('M','Hetero'):'F',
            ('M','Homo'):'M',
            
            ('F','Hetro'):'M',
            ('F','Homo'):'F',

            ('TM','Hetero'):'TF',
            ('TM','Homo'):'TM',

            ('TF','Hetero'):'TM',
            ('TF','Homo'):'TF',
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
        #create a dictionary to store matched preference
        matched_preferences = {}
        match_count = 0
        
        for queryset_attr, preference_key in preferences_to_check.items():
            queryset = getattr(user_preferences, queryset_attr).all()
            if queryset.exists():
                matched_preferences[preference_key] = [str(choice) for choice in queryset]
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
            
        preferences_filters = []

        for preference, queryset_name in preference_fields.items():
            queryset = getattr(user_preferences, queryset_name).all()
            if queryset.exists():
                field_name = f"{preference}__in"
                preferences_filters.append(Q(**{field_name: queryset}))

        # Add similar checks for other preference categories

        # Combine the Q objects using the OR operator (|)
        combined_filter = Q()
        for q_obj in preferences_filters:
            combined_filter |= q_obj

        # Query to find matching user profiles
        matching_profiles = UserProfile.objects.filter(combined_filter, user__gender=user_partner_gender_preference, user__orientation = user_orientation).exclude(user=user)

        # Serialize the matching user profiles
        serializer = UserProfileSerializer(matching_profiles, many=True)
        
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

        
        # Create a dictionary to store preferences by user ID
        preferences_by_user_id = {}


        current_date = datetime.now()
        for profile in matching_profiles:
            user_id = profile.user.id
            matches_count = 0
            print(f"user:{user_id}\n")
            # user_preferences = ProfilePreference.objects.get(user_profile=profile)
            preferences_by_user_id[user_id] = {}
            preferences_by_user_id[user_id]['id'] = profile.user.id
            preferences_by_user_id[user_id]['username'] = profile.user.username
            preferences_by_user_id[user_id]['interests'] = [interests.name for interests in profile.user.interests.all()]
            preferences_by_user_id[user_id]['date_of_birth'] = profile.user.date_of_birth
            age = current_date.year - profile.user.date_of_birth.year - ((current_date.month, current_date.day) < (profile.user.date_of_birth.month, profile.user.date_of_birth.day)) 
            preferences_by_user_id[user_id]['age'] =age
            preferences_by_user_id[user_id]['profile_picture'] = str(profile.profile_picture) if profile.profile_picture  else None
            preferences_by_user_id[user_id]['height'] = profile.height
            preferences_by_user_id[user_id]['languages'] = [language.name for language in profile.languages.all()]
            favorite_status = True if Favorite.objects.filter(user = profile, favored_by = user_profile).first() else False
            like_status = True if Like.objects.filter(user = profile, liked_by = user_profile).first() else False
            preferences_by_user_id[user_id]['favorite_status'] = favorite_status
            preferences_by_user_id[user_id]['like_status'] = like_status
            for field_name, choice_queryset in field_mapping.items():
                if choice_queryset.all():
                    for choice in choice_queryset.all():
                        profile_value = str(getattr(profile, field_name))
                        if profile_value == str(choice):
                            matches_count += 1
                            preferences_by_user_id[user_id][field_name] = profile_value
            print(f"choice count:{choice_count} matches count:{matches_count}")
            preferences_by_user_id[user_id]['match_percentage'] = (matches_count / choice_count)  * 100        
            match_percentage = ( matches_count / choice_count) * 100
            print(f"match percentage:{match_percentage}")
                            
        
        # return Response({'matching_profiles': serializer.data, 'preferences_by_user_id': preferences_by_user_id}, status=status.HTTP_200_OK)
        return Response({'preferences_by_user_id': preferences_by_user_id}, status=status.HTTP_200_OK)

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