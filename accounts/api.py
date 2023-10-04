from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from . models import User, UserProfile, CoverPhoto, Interest
from . serializers import UserSerializers, UpdateUserSerializer, UpdateUserProfileSerializer, CoverPhotoSerializer, UserProfileSerializer, InterestSerializer, CombinedSerializer
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.serializers import Serializer
import json
class GetUserData(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    
    @swagger_auto_schema(
    operation_description="Get user data",  # Describe the operation
    responses={200: UserProfileSerializer},  # Define the response schema
    tags=["User"],  # Categorize the endpoint using tags
    )
    def get(self, request):

        user = self.request.user
         
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
    def get(self, request):
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
            
            return Response({'status': True, 'message': 'Interest removed successfully'}, status=status.HTTP_204_NO_CONTENT)
            
        except User.DoesNotExist:
            print(f"ERROR:{e}")
            return Response({'status': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except Interest.DoesNotExist:
            print(f"ERROR:{e}")
            return Response({'status': False, 'message': 'Interest not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f"ERROR:{e}")
            return Response({'status': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)