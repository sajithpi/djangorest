from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from . models import UserProfile, CoverPhoto
from . serializers import UserSerializers, UpdateUserSerializer, UpdateUserProfileSerializer, CoverPhotoSerializer, UserProfileSerializer
from rest_framework import status
class GetUserData(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):

        user = self.request.user
         
         #get the user's profile 
        profile = UserProfile.objects.get(user=user)
        
        # Serialize profile data
        profile_serializer = UserProfileSerializer(profile)
        
        return Response(profile_serializer.data, status=status.HTTP_200_OK)
    
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
            
        except UserProfile.DoesNotExist:
            return Response({'error':'UserProfile does not exist for this user.'}, status=404)
        return Response({'message':'User Profile updated successfully'})
        # Return a success response
        return Response({'message': 'User information updated successfully'})
    

