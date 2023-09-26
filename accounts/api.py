from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
class SimpleApI(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):

        user = self.request.user

        user_details = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            # Add more fields as needed
        }

        return Response(user_details)
    
    def put(self, request):
        user = self.request.user
        user.first_name = request.data.get('first_name',user.first_name)
        user.last_name = request.data.get('last_name',user.last_name)
        user.save()
        # Return a success response
        return Response({'message': 'User information updated successfully'})