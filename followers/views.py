# from django.shortcuts import render
# from django.shortcuts import render
# from rest_framework.views import APIView
# from .serializers import FollowSerializer
# from rest_framework.response import Response
# from rest_framework import status, generics
# from rest_framework.generics import GenericAPIView
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
# from django.utils.http  import urlsafe_base64_encode, urlsafe_base64_decode
# from django.contrib.sites.shortcuts import get_current_site
# from django.urls import reverse
# from rest_framework.parsers import MultiPartParser
# from .models import Follower
# from django.shortcuts import get_object_or_404
# from accounts.models import User, UserProfile
# from drf_yasg import openapi
# from drf_yasg.utils import swagger_auto_schema
# import json
# # Create your views here.

# class FollowUser(GenericAPIView):

#     def post(self, request):
#         print(f"request data:{request.data}")
#         serializer = FollowSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'message':'success', 
#                          'description':'User follow action success'},
#                          status=status.HTTP_200_OK)
    
# class GetFollowData(GenericAPIView):
#     def post(self,request):
#         user_id = request.data.get('user_id')
        
#         # Ensure the user exists or return a 404 response if not found
#         user = get_object_or_404(User, id=user_id)
#         user_profile = UserProfile.objects.get(user = user)
#         # Calculate total followers and total following for the user
#         total_followers = Follower.objects.filter(following=user_profile).count()
#         total_following = Follower.objects.filter(follower=user_profile).count()
        
#         # Get the list of users following the current user
#         my_followers_list = Follower.objects.filter(following=user_profile).values_list('follower', flat=True)

#         #fetch username, and user profile picture of each user in the users_following_current_user list
#         followers_data = UserProfile.objects.filter(user__id__in=my_followers_list).values('user__username','user__id','profile_picture')

#         #get the list of users where the current user following
#         my_following_list = Follower.objects.filter(following=user_profile).values_list('following',flat=True)

#         #fetch username, and user profile picture of each user in the users_following_current_user list
#         following_data = UserProfile.objects.filter(user__id__in=my_following_list).values('user__username','user__id','profile_picture')

#         return Response({
#             'message': 'Success',
#             'description': 'User follow action success',
#             'total_followers': total_followers,
#             'total_following': total_following,
#             'users_followed_by_users': followers_data,
#             'following_data':following_data,
#         }, status=status.HTTP_200_OK)


from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import FavoriteSerializer
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
from .models import Favorite
from django.shortcuts import get_object_or_404
from accounts.models import User, UserProfile
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import json
# Create your views here.

class AddRemoveFavorite(GenericAPIView):

    def post(self, request):
        try:
            print(f"request data:{request.data}")
            user_id = request.data.get('user')
            favored_by = request.data.get('favored_by')
            user = UserProfile.objects.get(user = favored_by)
            favoured_user = UserProfile.objects.get(user = user_id)
            exists = Favorite.objects.filter(user = user, favored_by = favored_by)
            if exists:
                exists.delete()
                return Response({'status':'True', 
                                'message': f"{favoured_user.user.username} is already Favorited {user.user.username} so user in unfavored this user",
                                'action':f"{favoured_user.user.username}' is unfavorited {user.user.username}"
                                }, 
                                status=status.HTTP_200_OK)
            favorite = Favorite.objects.create(user = user, favored_by = favoured_user)
            favorite.save()
            print(f"user:{user} favored_user:{favoured_user}")
            return Response({'message':'Success', 
                            'description':f"{favoured_user.user.username} is Favorited {user.user.username} Successfully"},
                            status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
        
class GetFavoriteUsers(GenericAPIView):
    def post(self,request):
        user_id = request.data.get('user_id')
        
        # Ensure the user exists or return a 404 response if not found
        user = get_object_or_404(User, id=user_id)
        user_profile = UserProfile.objects.get(user = user)
        # Calculate total followers and total following for the user
        admire_count = Favorite.objects.filter(user=user_profile).count()
        my_favorites = Favorite.objects.filter(favored_by=user_profile).count()
        
        # Get the list of users following the current user
        my_admire_list = Favorite.objects.filter(user=user_profile).values_list('favored_by', flat=True)

        #fetch username, and user profile picture of each user in the users_following_current_user list
        my_admires_data = UserProfile.objects.filter(user__id__in=my_admire_list).values('user__username','user__id','profile_picture')

        #get the list of users where the current user following
        my_favorite_list = Favorite.objects.filter(favored_by=user_profile).values_list('user',flat=True)

        #fetch username, and user profile picture of each user in the users_following_current_user list
        my_favorite_data = UserProfile.objects.filter(user__id__in=my_favorite_list).values('user__username','user__id','profile_picture')

        return Response({
            'message': 'Success',
            'description': 'User follow action success',
            'admire_count': admire_count,
            'my_favorites': my_favorites,
            'my_admires_data': my_admires_data,
            'my_favorite_data':my_favorite_data,
        }, status=status.HTTP_200_OK)