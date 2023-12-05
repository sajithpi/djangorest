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
from django.conf import settings
from geopy.geocoders import Nominatim
from datetime import datetime

def get_country_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse(f"{latitude}, {longitude}")
    
    if location.raw.get("address"):
        country = location.raw["address"].get("country")
        if country:
            return country
    print("Country information not found")
    return 0

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
            
            
            print(f"TRIP:{user.username}")
            mutable_data = request.data.copy()
            mutable_data['user'] = user.id
            
            country = get_country_from_coordinates(mutable_data['latitude'], mutable_data['longitude'])
            if country:
                mutable_data['country'] = country
                
            print(f"MUTABLE DATA:{mutable_data}")
            serializer = MyTripSerializer(data=mutable_data, partial=True)

            if serializer.is_valid():
                # Save the validated data as a new TravelPlan instance
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
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
        try:
            user = User.objects.get(username=self.request.user)
            user_profile = UserProfile.objects.get(user=user)
            trip_id = request.data.get('trip_id')
            print(f"TRIP ID: {trip_id}")

            if trip_id is None:
                return Response({'error': 'trip_id is required for deleting.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                my_trip = MyTrip.objects.get(id=trip_id, user=user_profile)
            except MyTrip.DoesNotExist:
                return Response({'error': 'The specified trip does not exist.'}, status=status.HTTP_404_NOT_FOUND)

            my_trip.delete()
            return Response("Trip Deleted Successfully", status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
 
class RequestTrip(GenericAPIView):

    permission_classes = [IsAuthenticated, TwoFactorAuthRequired]
    @swagger_auto_schema(
        operation_summary="Request or cancel a trip",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'trip': openapi.Schema(type=openapi.TYPE_INTEGER, description='Trip ID'),
                # Add other properties from your request data here
            },
            required=['trip']
        ),
        responses={
            200: 'Trip requested or canceled successfully',
            400: 'Bad request. Validation errors may occur.',
            404: 'User, user profile, or trip not found.',
            500: 'Internal Server Error'
        },
        tags=["Travel"]
        
    )
    def post(self, request):
        try:
            user = User.objects.get(username=request.user)
            user_profile = UserProfile.objects.get(user=user)
            trip = MyTrip.objects.get(id=request.data.get('trip'))

            mutable_data = request.data.copy()
            mutable_data['requested_user'] = user_profile.id
            mutable_data['trip'] = trip.id

            try:
                # Check if a travel request for the specified trip and user exists
                check_trip_exists = TravelRequest.objects.get(trip=trip, requested_user=user_profile)
                
                if check_trip_exists:
                    check_trip_exists.delete()
                    return Response({'status':'cancel','message': 'Trip Request canceled successfully'}, status=status.HTTP_200_OK)
            except TravelRequest.DoesNotExist:
                # The specified travel request does not exist, continue with creating a new one
                pass
            
            serializer = TripRequestSerializer(data=mutable_data, context={'request': request}, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({'status': 'request', 'message': 'Trip requested successfully'}, status=status.HTTP_200_OK)
            else:
                # Return a response with validation errors
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        except MyTrip.DoesNotExist:
            return Response({'error': 'Trip not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class ListTrips(GenericAPIView):
    
    def get_request_status(self, trip_id, user_id):
        try:
            user = User.objects.get(id=user_id)
            print(f"get_request_status")
            print(f"user:{user}")
            user_profile = UserProfile.objects.get(user=user)
            trip = MyTrip.objects.get(id=trip_id)
            status = TravelRequest.objects.get(trip=trip, requested_user=user_profile)
            
            print(f"REQUEST STATUS: get_request_status{status} trip:{trip_id}")
            return True
        # except User.DoesNotExist:
        #     raise Http404("User not found.")
        # except UserProfile.DoesNotExist:
        #     raise Http404("User profile not found.")
        # except MyTrip.DoesNotExist:
        #     raise Http404("Trip not found.")
        except TravelRequest.DoesNotExist:
            print(f"TravelRequest Does't exist")
            return False  # TravelRequest not found, returning False
    
    @swagger_auto_schema(
        operation_summary="List Matching Trips",
        operation_description="Get a list of matching trips based on user preferences.",
        manual_parameters=[
            openapi.Parameter(
                name="type",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description="The type of trip you are looking for (e.g., 'dating').",
                required=False,
            ),
            openapi.Parameter(
                name="location",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description="The location you are interested in (e.g., 'any').",
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of matching trips",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "trip list": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "user": openapi.Schema(type=openapi.TYPE_STRING),
                                    "trip_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "profile_picture": openapi.Schema(type=openapi.TYPE_STRING),
                                    "days": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "description": openapi.Schema(type=openapi.TYPE_STRING),
                                    "date": openapi.Schema(type=openapi.TYPE_STRING),
                                    "status": openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                        ),
                    },
                ),
            ),
            400: "Bad Request",
        },
        tags=["Travel"],
    )
    def get(self, request):
        try:
            
            user = User.objects.get(username = self.request.user)
            user_profile = UserProfile.objects.get(user = user)
            user_gender = user_profile.user.gender
            user_orientation = user_profile.user.orientation
            
            NOW = settings.NOW
            
            travel_type = request.headers.get('type','dating')
            location = request.headers.get('location', 'any')
            trip_date_range = request.headers.get('tripdate', '')
            print(f"trip_date_range:{trip_date_range}")
            try:
                trip_date_range = datetime.strptime(trip_date_range,'%Y-%m-%d')
                # Set the time components to 23:59:59
                trip_date_range = trip_date_range.replace(hour=23, minute=59, second=59)
      
                print(f"trip_date_range:{trip_date_range}")
            except Exception as e:
                trip_date_range = ''
            
            if travel_type == '':
                travel_type = 'dating'
            if location == '':
                location = 'any'
            
            print(f'travel_type:{request.headers.get("type")}')
            print(f'Location:{request.headers.get("location")}')
            print(f"trip_date:{trip_date_range}")
            
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
                looking_for = travel_type,
                travel_date__gte = NOW,
                
                status = 'planning',
                    ).exclude(user = user_profile,)
            
            if location != 'any':
                matching_Trips = matching_Trips.filter(location = location.lower())
            
            if travel_type == 'dating':
                # matching_Trips = matching_Trips.filter(user__user__gender=user_partner_gender_preference,
                # user__user__orientation=user_orientation)
                matching_Trips = matching_Trips.filter(
                user__user__orientation=user_orientation)
                
            if trip_date_range != '':
                matching_Trips = matching_Trips.filter(travel_date__lte = trip_date_range)
            
            
            trip_list = []
            if matching_Trips:
                for matching_Trip in matching_Trips:
                    trip = {}
                    trip['user'] = matching_Trip.user.user.username
                    trip['user_id'] = matching_Trip.user.user.id
                    trip['trip_id'] = matching_Trip.id
                    trip['request_status'] = self.get_request_status(matching_Trip.id, user.id)
                    trip['location'] = matching_Trip.location
                    trip['profile_picture'] = str(matching_Trip.user.profile_picture)
                    trip['days'] = matching_Trip.days
                    trip['description'] = matching_Trip.description
                    trip['date'] = matching_Trip.travel_date
                    trip['status'] = matching_Trip.status
                    
                    trip_list.append(trip)
                    
            print(f"matching trip:{matching_Trips}")
            
           
            return Response({"trip_list": trip_list}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"error:{e}")
            return Response(f"error:{str(e)}", status=status.HTTP_400_BAD_REQUEST)
        
