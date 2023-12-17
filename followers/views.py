from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import FavoriteSerializer, RatingSerializer
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
from .models import Favorite, Like, BlockedUser, Poke, CoverPhoto, Rating
from django.db.models import F, Func, ExpressionWrapper, DateTimeField
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q
from accounts.models import User, UserProfile
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import json
from accounts.api import get_blocked_users_data, add_notification, remove_notification
# Create your views here.
"""_summary_
    First two classes for Favorites
    Returns:
        _type_: Favorite 
"""
class AddRemoveFavorite(GenericAPIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="The ID of the user to favorite/unfavorite."
                ),
            },
            required=['user'],
        ),
        responses={
            200: "Favorite/unfavorite action was successful",
            400: "Bad request or user is already favorited/unfavorited",
            500: "Internal server error",
        },
        tags=["Favorite"],
    )
    def post(self, request):
        """
        Favorite/Unfavorite a user.
        """
        try:
            print(f"request data:{request.data}")
            user = request.data.get('user')
            favored_by = UserProfile.objects.get(user__id = request.user.id)
            user = UserProfile.objects.get(user = user)
            # favoured_user = UserProfile.objects.get(user = favored_by)
            exists = Favorite.objects.filter(user = user, favored_by = favored_by).first()
            
            if exists:
                exists.delete()
                
                remove_notification(from_user = favored_by, to_user=user, type='follow')
                return Response({'status':'True', 
                                'message': f"{favored_by.user.username} is already Favorited {user.user.username} so user in unfavored this user",
                                'action':f"{favored_by.user.username}' is unfavored {user.user.username}"
                                }, 
                                status=status.HTTP_200_OK)
            favorite = Favorite.objects.create(user = user, favored_by = favored_by)
            favorite.save()
            description = f"{favored_by.user.username} is Favorited {user.user.username}'"
            
            add_notification(from_user=favored_by, to_user=user, type='follow', description=description)
            print(f"user:{user} favored_user:{request.user}")
            return Response({'message':'Success', 
                            'description':f"{description} Successfully"},
                            status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
# Calculate age based on date of birth
def calculate_age(date_of_birth):
    now = settings.NOW
    today = now
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    return age
        
class GetFavoriteUsers(GenericAPIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            200: "Successful response with admire count and favorite user data",
            404: "User not found",
        },
        tags=["Favorite"],
    )
   

    def get(self, request):
        """
        Get favorite users and admire count. Note:User Must be login
        """
        user_id = request.user.id
        
        # Ensure the user exists or return a 404 response if not found
        user = get_object_or_404(User, id=user_id)
        user_profile = UserProfile.objects.get(user = user)
        blocked_users = get_blocked_users_data(user_profile=user_profile)
        print(f"blocked_users:{blocked_users}")
        # Calculate total followers and total following for the user
        admire_count = Favorite.objects.filter(user=user_profile).count()
        my_favorites = Favorite.objects.filter(favored_by=user_profile).count()
        
        
        
        # Get the list of users following the current user
        my_admire_list = Favorite.objects.filter(user=user_profile).values_list('favored_by', flat=True)

    
        #fetch username, and user profile picture of each user in the users_following_current_user list
        # my_admires_data = UserProfile.objects.filter(user__id__in=my_admire_list)\
        #                                     .annotate(
        #                                         age = ExpressionWrapper(
        #                                             Func(now - F('user__date_of_birth'), function = 'DATE_PART', template = 'year'),
        #                                             output_field=DateTimeField()
        #                                             )
        #                                         )\
        #                                     .values('user__username','user__id','profile_picture', 'age').exclude(user__id__in=blocked_users)
        my_admires_data = UserProfile.objects.filter(user__id__in=my_admire_list)\
                                            .values('user__username','user__id','profile_picture', 'user__date_of_birth').exclude(user__id__in=blocked_users)
        
        for user_data in my_admires_data:
            date_of_birth = user_data['user__date_of_birth']
            if date_of_birth:
                user_data['age'] = calculate_age(date_of_birth)
        
        #get the list of users where the current user following
        my_favorite_list = Favorite.objects.filter(favored_by=user_profile).values_list('user',flat=True)

        #fetch username, and user profile picture of each user in the users_following_current_user list
        my_favorite_data = UserProfile.objects.filter(user__id__in=my_favorite_list).values('user__username','user__id','profile_picture', 'user__date_of_birth').exclude(user__id__in=blocked_users)

        for user_data in my_favorite_data:
            date_of_birth = user_data['user__date_of_birth']
            if date_of_birth:
                user_data['age'] = calculate_age(date_of_birth)
        return Response({
            'message': 'Success',
            'description': 'User follow action success',
            'admire_count': admire_count,
            'my_favorites': my_favorites,
            'my_admires_data': my_admires_data,
            'my_favorite_data':my_favorite_data,
        }, status=status.HTTP_200_OK)
    
"""_summary_: Classes For LIking
"""
class LikeDislike(GenericAPIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="The ID of the user to like/dislike."
                ),
            },
            required=['user'],
            
        ),
        responses={
            200: "Like/Dislike action was successful",
            400: "Bad request or user is already Liked",
            500: "Internal server error",
        },
        tags=["Like"],
    )
    def post(self, request):
        """
        Like/Dislike a user. This is a view for liking or disliking a user profile.
        """
        try:
            # Print the request data for debugging purposes
            print(f"request data:{request.data}")
            
            # Get the user to be liked/disliked from the request data
            user = request.data.get('user')
            
            # Get the UserProfile of the user who is performing the action (the one liking/disliking)
            liked_by = UserProfile.objects.get(user__id=request.user.id)
            
            # Get the UserProfile of the user being liked/disliked
            user = UserProfile.objects.get(user=user)
            
            # Check if a 'Like' entry already exists for the given user and liker
            exists = Like.objects.filter(user=user, liked_by=liked_by).first()
            
            if exists:
                # If a 'Like' entry already exists, delete it (dislike)
                exists.delete()
                
                # Remove the notification related to the dislike action
                remove_notification(from_user=liked_by, to_user=user, type='like')
                
                return Response({'status': 'True', 
                                'action': f"{liked_by.user.username} disliked {user.user.username}"
                                }, 
                                status=status.HTTP_200_OK)
            else:
                # If a 'Like' entry does not exist, create a new one (like)
                like = Like.objects.create(user=user, liked_by=liked_by)
                like.save()
                
                # Create a description for the like action
                description = f"{liked_by.user.username} is liked {user.user.username}"
                
                # Add a notification for the like action
                add_notification(from_user=liked_by, to_user=user, type='like', description=description)
                
                # Print user and favored_user for debugging purposes
                print(f"user:{user} favored_user:{request.user}")
                
                return Response({'message': 'Success', 
                                'description': f"{liked_by.user.username} liked {user.user.username} Successfully"
                                },
                                status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist as e:
            # Handle the case where the UserProfile does not exist
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetLikeUsers(GenericAPIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            200: "Successful response with admire count and favorite user data",
            404: "User not found",
        },
        tags=["Like"],
    )
    def get(self, request):
        """
        Get favorite users and admire count. Note: User must be logged in.
        """
        user_id = request.user.id
        
        # Ensure the user exists or return a 404 response if not found
        user = get_object_or_404(User, id=user_id)
        user_profile = UserProfile.objects.get(user = user)
        # Calculate total likes you got and your likes 
        admire_count = Like.objects.filter(user=user_profile).count()
        my_likes = Like.objects.filter(liked_by=user_profile).count()

        blocked_users = get_blocked_users_data(user_profile=user_profile)

        # Get the list of users liked the current user
        my_admire_list = Like.objects.filter(user=user_profile).values_list('liked_by', flat=True)

        #fetch username, and user profile picture of each user in the users_liked current_user list
        my_admires_data = UserProfile.objects.filter(user__id__in=my_admire_list).values('user__username','user__id','profile_picture', 'user__date_of_birth').exclude(user__id__in=blocked_users)
        for user_data in my_admires_data:
            date_of_birth = user_data['user__date_of_birth']
            if date_of_birth:
                user_data['age'] = calculate_age(date_of_birth)
        #get the list of users where the current user liked
        my_like_list = Like.objects.filter(liked_by=user_profile).values_list('user',flat=True)

        #fetch username, and user profile picture of each user in the user liked  list
        my_like_data = UserProfile.objects.filter(user__id__in=my_like_list).values('user__username','user__id','profile_picture','user__date_of_birth').exclude(user__id__in=blocked_users)
        
        for user_data in my_like_data:
            date_of_birth = user_data['user__date_of_birth']
            if date_of_birth:
                user_data['age'] = calculate_age(date_of_birth)
        return Response({
            'message': 'Success',
            'admire_count': admire_count,
            'my_likes': my_likes,
            'my_admires_users': my_admires_data,
            'my_like_data':my_like_data,
        }, status=status.HTTP_200_OK)
    

class BLockUser(GenericAPIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            200: "Successful response with block/unblock message",
            404: "User not found",
        },
        tags=["Block"],
    )
    def post(self, request):
        """
        Block or unblock a user. Note: User must be logged in.
        """
        try:
            # Print the request data for debugging purposes
            print(f"request data:{request.data}")
            
            # Get the user to be blocked/unblocked from the request data
            user = request.data.get('user')
            report_status = request.data.get('report_status',3)
            report_description = request.data.get('report_description','block')
            ip_address = request.META.get('REMOTE_ADDR')
            # Get the UserProfile of the user who is performing the action (the one blocking/unblocking)
            blocked_by = UserProfile.objects.get(user__id=request.user.id)
            
            # Get the UserProfile of the user being blocked/unblocked
            user = UserProfile.objects.get(user=user)
            
            # Check if a 'BlockedUser' entry already exists for the given user and blocker
            blocked_user = BlockedUser.objects.filter(user=user, blocked_by=blocked_by).first()
            
            if blocked_user:
                # If a 'BlockedUser' entry already exists, delete it (unblock)
                blocked_user.delete()
                
                return Response({'status': 'True', 
                                'action': f"{blocked_by.user.username} is unblocked {user.user.username}"
                                }, 
                                status=status.HTTP_200_OK)
            else:
                # If a 'BlockedUser' entry does not exist, create a new one (block)
                block_user = BlockedUser.objects.create(user=user, 
                                                        blocked_by=blocked_by,
                                                        report_status = report_status,
                                                        description = report_description,
                                                        ip_address = ip_address)
                block_user.save()
                
                # Remove favorite entries related to either user
                remove_favorite = Favorite.objects.filter(
                    Q(user=user) | Q(user=blocked_by),
                    Q(favored_by=blocked_by) | Q(favored_by=user)
                )
                remove_favorite.delete()
                
                # Remove like entries related to either user
                remove_likes = Like.objects.filter(
                    Q(user=user) | Q(user=blocked_by),
                    Q(liked_by=blocked_by) | Q(user=user)
                )
                remove_likes.delete()
                
                return Response({'message': 'Success', 
                                'description': f"{blocked_by.user.username} blocked {user.user.username} Successfully"
                                },
                                status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist as e:
            # Handle the case where the UserProfile does not exist
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetBlockedUsers(GenericAPIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            200: "Successful response with blocked users' data",
            404: "User not found",
        },
        tags=["Block"],
    )
    def get(self, request):
        """
        Get blocked users. Note: User must be logged in.
        """    
        user_id = request.user.id
        
        # Ensure the user exists or return a 404 response if not found
        user = get_object_or_404(User, id=user_id)
        user_profile = UserProfile.objects.get(user = user)
        
        my_blocked_user_count = BlockedUser.objects.filter(blocked_by=user_profile).count()
        
    
        #get the list of users where the current user blocked
        my_blocked_list = BlockedUser.objects.filter(blocked_by=user_profile).values_list('user',flat=True)

        #fetch username, and user profile picture of each user in the user liked  list
        my_blocked_users_data = UserProfile.objects.filter(user__id__in=my_blocked_list).values('user__username','user__id','profile_picture')

        return Response({
            'message': 'Success',
            'my_blocked_user_count': my_blocked_user_count,
            'my_blocked_users_data':my_blocked_users_data,
        }, status=status.HTTP_200_OK)
    

class ReportUsers(GenericAPIView):
    def get(self, request):
        
        user = User.objects.get(username = request.user)
        print(f"USER ADMIN STATUS:{user.is_admin}")
        if not user.is_admin:
            return Response("You don't have privilege to access this api", status = status.HTTP_400_BAD_REQUEST)
        
        report_status = request.data.get('report_status',3)
        if report_status == 3:
            return Response({'message':'You have to pass report_status id'}, status = status.HTTP_400_BAD_REQUEST)
        reported_users = BlockedUser.objects.filter(report_status = report_status).all()
        reported_users_list = []
        for reported_user in reported_users:
            reported_users_dict = {
                'id':reported_user.id,
                'user':reported_user.user.user.username,
                'reported_by':reported_user.blocked_by.user.username,
                'ip_address':reported_user.ip_address
            }
            reported_users_list.append(reported_users_dict)

        return Response(reported_users_list, status = status.HTTP_200_OK)

    def put(self, request):
        
        user = User.objects.get(username = request.user)
        
        if not user.is_admin:
            return Response("You don't have privilege to access this api", status = status.HTTP_400_BAD_REQUEST)
        
        report_id = request.data.get('report_id')
        report_status = request.data.get('report_status')
        
        if not report_id:
            return Response(f"You have to pass report id", status = status.HTTP_400_BAD_REQUEST)
        if not report_status:
            return Response(f"You have to pass report status", status.status.HTTP_400_BAD_REQUEST)
        
        report = BlockedUser.objects.get(id = report_id)
        report.report_status = report_status
        report.save()

        return Response({'message':"Successfully Updated"}, status = status.HTTP_200_OK)
        
class PokeUser(GenericAPIView):
 
    def post(self, request):
        """
        This view is used to perform a 'poke' action on a user.
        """
        try:
            # Print the request data for debugging purposes
            print(f"request data:{request.data}")
            
            # Get the user to be poked from the request data
            user = request.data.get('user')
            
            # Get the UserProfile of the user who is performing the action (the one poking)
            poked_by = UserProfile.objects.get(user__id=request.user.id)
            
            # Get the UserProfile of the user being poked
            user = UserProfile.objects.get(user=user)
            
            # Create a 'Poke' entry to record the poke action
            poke = Poke.objects.create(user=user, poked_by=poked_by)
            poke.save()
            
            # Create a description for the poke action
            description = f"{poked_by.user.username} is poked {user.user.username}"
            
            # Add a notification for the poke action
            add_notification(from_user=poked_by, to_user=user, type='poke', description=description)
            
            # Print user and poked information for debugging purposes
            print(f"user:{user} poked:{request.user}")
            
            return Response({'message': 'Success', 
                            'description': f"{poked_by.user.username} poked {user.user.username} Successfully"
                            },
                            status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist as e:
            # Handle the case where the UserProfile does not exist
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetPokedUsers(GenericAPIView):
    
    def get(self, request):
            """
            Get favorite users and admire count. Note: User must be logged in.
            """
            user_id = request.user.id
            
            # Ensure the user exists or return a 404 response if not found
            user = get_object_or_404(User, id=user_id)
            user_profile = UserProfile.objects.get(user = user)
            # Calculate total pokes you got and your pokes 
            poked_me_count = Poke.objects.filter(user=user_profile).count()
            my_pokes = Poke.objects.filter(liked_by=user_profile).count()

            blocked_users = get_blocked_users_data(user_profile=user_profile)

            # Get the list of users poked the current user
            poked_me_list = Poke.objects.filter(user=user_profile).values_list('poked_by', flat=True)

            #fetch username, and user profile picture of each user in the users_poked current_user list
            users_who_poked_me = UserProfile.objects.filter(user__id__in=poked_me_list).values('user__username','user__id','profile_picture', 'user__date_of_birth').exclude(user__id__in=blocked_users)
            for user_data in users_who_poked_me:
                date_of_birth = user_data['user__date_of_birth']
                if date_of_birth:
                    user_data['age'] = calculate_age(date_of_birth)
            #get the list of users where the current user poked
            my_poke_list = Like.objects.filter(liked_by=user_profile).values_list('user',flat=True)

            #fetch username, and user profile picture of each user in the user poked  list
            my_poke_data = UserProfile.objects.filter(user__id__in=my_poke_list).values('user__username','user__id','profile_picture','user__date_of_birth').exclude(user__id__in=blocked_users)
            
            for user_data in my_poke_data:
                date_of_birth = user_data['user__date_of_birth']
                if date_of_birth:
                    user_data['age'] = calculate_age(date_of_birth)
            return Response({
                'message': 'Success',
                'poked_me_count': poked_me_count,
                'my_pokes': my_pokes,
                'users_who_poked_me': users_who_poked_me,
                'my_poke_data':my_poke_data,
            }, status=status.HTTP_200_OK)
        
class RateUserCoverPhoto(GenericAPIView):
    
    
    def post(self, request):
        try:
            # Get the User object for the user making the request
            rated_user = User.objects.get(username=request.user)
            
            # Get the UserProfile object associated with the rated user
            rated_user_profile = UserProfile.objects.get(user=rated_user)
            
            # Get the User object for the user to be rated (from the request data)
            user = User.objects.get(username=request.data.get('username'))
            
            # Get the UserProfile object associated with the user to be rated
            user_profile = UserProfile.objects.get(user=user)
            
            # Get the ID of the cover photo from the request data
            cover_photo_id = request.data.get('cover_photo')
            
            # Get the CoverPhoto object using the cover photo ID
            cover_photo = CoverPhoto.objects.get(id=cover_photo_id)
            
            # Print the cover photo link for debugging purposes
            print(f"cover photo link:{cover_photo.image}")
            
            # Get the rating count from the request data
            rating_count = request.data.get('rate_count')
            
            
            # Check if a rating entry already exists for the given user, rated user, and cover photo
            existing_rating = Rating.objects.filter(user = user_profile, rated_by = rated_user_profile, cover_photo = cover_photo)
            if existing_rating:
                print(f"already exists")
                existing_rating.rate_count = rating_count
                print(f"rate:{existing_rating.rate_count}")
                existing_rating.update()
            else:
                print(f"creating new rating")
                # Create a new Rating entry to record the rating
                Rating.objects.create(user=user_profile, rated_by=rated_user_profile, cover_photo=cover_photo, rate_count=rating_count)
            # Add a notification for the raging action
          
            add_notification(from_user=rated_user_profile, to_user=user_profile, type='poke', description=rating_count)
            
            return Response({'message': 'Cover Photo Rating Successful'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Handle the case where the user does not exist
            return Response({'error': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            # Handle the case where the user profile does not exist
            return Response({'error': 'User profile does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except CoverPhoto.DoesNotExist:
            # Handle the case where the cover photo does not exist
            return Response({'error': 'Cover photo does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Handle other exceptions with a generic error message
            return Response({'error': f"Error: {e}"}, status=status.HTTP_400_BAD_REQUEST)