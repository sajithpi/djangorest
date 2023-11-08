from django.shortcuts import render
from . models import TravelAim, MyTrip, TravelRequest
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from accounts.api import TwoFactorAuthRequired
from rest_framework import status, permissions
from . serializers import TravelAimSerializers, MyTripSerializer, TripRequestSerializer
from accounts.models import User, UserProfile
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from accounts.api import get_blocked_users_data
from django.db.models import Q

# Create your views here.

class TravelLookingFor(GenericAPIView):
    permission_classes = [IsAuthenticated, TwoFactorAuthRequired]

    def get(self, request):
        travel_aims = TravelAim.objects.all()
        device = request.query_params.get('device')
        print(f"device:{device}")
        travel_aims_serializer = TravelAimSerializers(travel_aims, many = True, context = {'request':request})
        return Response(travel_aims_serializer.data, status = status.HTTP_200_OK)
    
class TravelPlan(GenericAPIView):
    permission_classes = [IsAuthenticated, TwoFactorAuthRequired]
    
 
    @swagger_auto_schema(
        operation_description="Retrieve a list of the user's travel plans.",
        responses={
            200: MyTripSerializer(many=True),
            400: "Bad Request",
        },
        tags=["Travel"]
    )

    def get(self, request):
        try:
            user = User.objects.get(username = self.request.user)
            user_profile = UserProfile.objects.get(user = user)

            my_trips = MyTrip.objects.filter(user = user_profile)
            serializer = MyTripSerializer(data= my_trips, many = True)
            
            serializer.is_valid()
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"ERROR:{e}")
            return Response(f"error:{str(e)}", status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
        request_body=MyTripSerializer,
        operation_description="Create a new TravelPlan.",
        responses={
            201: MyTripSerializer,
            400: "Bad Request",
            500: "Internal Server Error",
        },
        tags=["Travel"]
    )
    def post(self, request):
        """
        Create a new TravelPlan.
        """
        try:
            user = User.objects.get(username=request.user)
            user_profile = UserProfile.objects.get(user=user)
            mutable_data = request.data.copy()
            mutable_data['user'] = user.id
            serializer = MyTripSerializer(data=mutable_data, partial=True)

            if serializer.is_valid():
                # Save the validated data as a new TravelPlan instance
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any other exceptions that might occur
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        request_body=MyTripSerializer,
        operation_description="Update an existing TravelPlan using 'trip_id' provided in the request body.",
        responses={
            200: MyTripSerializer,
            400: "Bad Request",
            404: "Not Found",
            500: "Internal Server Error",
        },
        tags=["Travel"]
    )
    def put(self, request):
        """
        Update an existing TravelPlan using 'travel_id'.
            - trip_id (integer, required): ID of the TravelPlan to update.
        """
        try:
            # Extract 'travel_id' from the request data
            travel_id = request.data.get('trip_id')

            # Check if a 'travel_id' is provided in the request
            if travel_id is not None:
                user = User.objects.get(username=request.user)
                travel_plan = MyTrip.objects.get(id=travel_id)

                # Copy the request data and set the 'user' field to the user's ID
                mutable_data = request.data.copy()
                mutable_data['user'] = user.id

                # Serialize the data and update the existing TravelPlan
                serializer = MyTripSerializer(travel_plan, data=mutable_data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'trip_id is required for updating.'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except MyTrip.DoesNotExist:
            return Response({'error': 'TravelPlan not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
    
    @swagger_auto_schema(
        operation_description="Delete a TravelPlan by specifying 'trip_id' in the request data.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'trip_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the TravelPlan to delete."),
            },
            required=['trip_id'],
        ),
        responses={
            200: "Trip Deleted Successfully",
            400: "Bad Request",
            404: "Not Found",
            500: "Internal Server Error",
        },
        tags=["Travel"]
    )
    def delete(self, request):
        
        user = User.objects.get(username = self.request.user)
        user_profile = UserProfile.objects.get(user = user)
        trip_id = request.data.get('trip_id')
        
        if trip_id is None:
            return Response({'error': 'trip_id is required for deleting.'}, status=status.HTTP_400_BAD_REQUEST)
        
        my_trip = MyTrip.objects.get(id = trip_id, user = user_profile) 
        if my_trip:
            my_trip.delete()
        
        return Response(f"Trip Deleted Successfully", status=status.HTTP_200_OK)
        
        
 
class RequestTrip(GenericAPIView):

    permission_classes = [IsAuthenticated, TwoFactorAuthRequired]

    def post(self, request):
        # try:
            user = User.objects.get(username = request.user)
            user_profile = UserProfile.objects.get(user = user)
            trip = MyTrip.objects.get(id = request.data.get('trip'))
            # travel_request = TravelRequest.objects.create(trip=trip, requested_user = user_profile,)
            # return Response({"message": "Travel request created successfully"}, status=status.HTTP_201_CREATED)

            mutable_data = request.data.copy()
            mutable_data['requested_user'] = user_profile.id
            mutable_data['trip'] = trip.id
            
             # Check if a travel request for the specified trip and user exists
            check_trip_exists = TravelRequest.objects.get(trip = trip, requested_user = user_profile)
            
            if check_trip_exists:
                check_trip_exists.delete()
                return Response({'message':'Trip Request cancelled successfully'}, status=status.HTTP_200_OK)
            
            serializer = TripRequestSerializer(data = mutable_data, context = {'request':request}, partial = True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({'status':True, 'message':'trip requested successfully'},status=status.HTTP_200_OK)
            else:
                 # Return a response with validation errors
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

class ListTrips(GenericAPIView):
    
    def get(self, request):
        try:
            user = User.objects.get(username = self.request.user)
            user_profile = UserProfile.objects.get(user = user)
            user_gender = user_profile.user.gender
            user_orientation = user_profile.user.orientation
            
            
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
            
            blocked_users = get_blocked_users_data(user_profile=user_profile)
            
            exclude_blocked_users = Q(user__id__in=blocked_users)
            
            matching_Trips = MyTrip.objects.filter(
                ~exclude_blocked_users,
                user__user__gender=user_partner_gender_preference,
                user__user__orientation=user_orientation,
                status = 'planning',
                    ).exclude(user = user_profile)
            
            
            
            trip_list = []
            if matching_Trips:
                for matching_Trip in matching_Trips:
                    trip = {}
                    trip['user'] = matching_Trip.user.user.username
                    trip['trip_id'] = matching_Trip.id
                    trip['profile_picture'] = str(matching_Trip.user.profile_picture)
                    trip['days'] = matching_Trip.days
                    trip['description'] = matching_Trip.description
                    trip['date'] = matching_Trip.travel_date
                    trip['status'] = matching_Trip.status
                    
                    trip_list.append(trip)
                    
            print(f"matching trip:{matching_Trips}")
            
           
            return Response({"trip list": trip_list}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"error:{e}")
            return Response(f"error:{str(e)}", status=status.HTTP_400_BAD_REQUEST)