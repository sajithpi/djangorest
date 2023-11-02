from django.shortcuts import render
from . models import TravelAim
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from accounts.api import TwoFactorAuthRequired
from rest_framework import status, permissions
from . serializers import TravelAimSerializers, TravelPlanSerializer, TripRequestSerializer
from accounts.models import User, UserProfile

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

    def post(self, request):
        try:
            user = User.objects.get(username = request.user)
            user_profile = UserProfile.objects.get(user = user)
            mutable_data = request.data.copy()
            mutable_data['user'] = user.id
            serializer = TravelPlanSerializer(data = mutable_data, partial = True)
            
            if serializer.is_valid():
                # Save the validated data as a new TravelPlan instance
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any other exceptions that might occur
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RequestTrip(GenericAPIView):

    permission_classes = [IsAuthenticated, TwoFactorAuthRequired]

    def post(self, request):
        # try:
            user = User.objects.get(username = request.user)
            user_profile = UserProfile.objects.get(user = user)
            mutable_data = request.data.copy()
            mutable_data['requested_user'] = user_profile.id
            serializer = TripRequestSerializer(data = mutable_data, context = {'request':request}, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response({'status':True, 'message':'trip requested successfully'},status=status.HTTP_200_OK)
            else:
                 # Return a response with validation errors
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request):
        user = User.objects.get(username = request.user)
        mutable_data = request.data.copy()
        mutable_data['requested_user'] = user.id
        serializer = TripRequestSerializer(data = mutable_data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':True, 'message':'trip requested successfully'},status=status.HTTP_200_OK)
