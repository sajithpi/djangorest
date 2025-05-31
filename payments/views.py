from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from accounts.models import Package, User
from django.conf import settings
from django.http import JsonResponse
from . paypal import generate_access_token
from rest_framework.permissions import BasePermission

import requests
# Create your views here.


PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
PAYPAL_CLIENT_SECRET = settings.PAYPAL_CLIENT_SECRET
PAYPAL_BASE_URL = settings.PAYPAL_BASE_URL



class IsAdminUserAuthenticated(BasePermission):
    """
    Allows access only to authenticated users who are also admins.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'is_admin', False)
    
    

class GetClientId(GenericAPIView):
    def get(self, request):
        return Response(PAYPAL_CLIENT_ID, status=status.HTTP_200_OK)
    
class Product(GenericAPIView):
    
    permission_classes = [IsAdminUserAuthenticated]
    
    def post(self, request):
        access_token = generate_access_token()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'PayPal-Request-Id': 'PRODUCT-18062019-001',
            'Prefer': 'return=representation',
        }

        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_details = Package.objects.get(id=product_id)
        except Package.DoesNotExist:
            return Response({'error': 'Package not found'}, status=status.HTTP_404_NOT_FOUND)

        if product_details.type == 'Free':
            return Response('Only Paid Products support for the subscription plan', status=status.HTTP_406_NOT_ACCEPTABLE)

        if not product_details.price or not product_details.validity:
            return Response(
                f'Please check the validity and price of the product, Validity:{product_details.validity}, Price:{product_details.price}',
                status=status.HTTP_412_PRECONDITION_FAILED
            )

        # Prepare PayPal product data
        data = {
            "name"          : product_details.name,
            "description"   : "dating pack",
            "type"          : "SERVICE",
            "category"      : "SOFTWARE"
        }

        response = requests.post(
            f'https://{PAYPAL_BASE_URL}/v1/catalogs/products',
            headers=headers,
            json=data
        )

        if response.status_code in [200, 201]:
            data = response.json()
            paypal_product_id = data.get('id')
            product_details.paypal_product_id = paypal_product_id
            product_details.save()  # ✅ Save to DB
            return JsonResponse(data, safe=False)
        else:
            print(f"PayPal API error: {response.status_code} - {response.text}")
            return Response({
                "message": "Failed to create product on PayPal",
                "paypal_response": response.json()
            }, status=response.status_code)
            
    def get(self, request):
        access_token = generate_access_token()
        page_size = request.data.get('page_size',2)
        page      = request.data.get('page',1)
        
        headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
        }

        params = (
            ('page_size', page_size),
            ('page', page),
            ('total_required', 'true'),
        )
        response = requests.get(f'https://{PAYPAL_BASE_URL}/v1/catalogs/products', headers=headers, params=params)
        
        if response.status_code == 200:
            return Response(response.json(), status=response.status_code)
        else:
            print(f"PayPal API error: {response.status_code} - {response.text}")
            return Response({
                "message": "Failed to create product on PayPal",
                "paypal_response": response.json()
            }, status=response.status_code)