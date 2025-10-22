from time import timezone
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from accounts.models import Package, User
from django.conf import settings
from django.http import JsonResponse
from . paypal import generate_access_token
from rest_framework.permissions import BasePermission, IsAuthenticated
from datetime import datetime, timezone
from django.shortcuts import get_object_or_404

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
    

class ProductPlanView(GenericAPIView):
    permission_classes = [IsAdminUserAuthenticated]
    

    def post(self, request):
        access_token = generate_access_token()
        print("Access Token:", access_token)  # Debugging line
        
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product_details = Package.objects.only('id', 'type', 'paypal_product_id','validity').get(id=product_id)

            if product_details.type == 'Free':
                return Response('Only Paid Products support for the subscription plan', status=status.HTTP_406_NOT_ACCEPTABLE)
            
            product_validity = 30 * int(product_details.validity)

            package_paypal_id = product_details.paypal_product_id
            print("Package PayPal ID:", package_paypal_id)  # Debugging line
            plan_response = self.create_product_validity_day_plan(package_paypal_id, product_validity, access_token)
            if not plan_response:
                return Response({'error': 'Failed to create plan on PayPal'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            paypal_plan_id = plan_response.get('id')
            product_details.paypal_plan_id = paypal_plan_id
            product_details.save(update_fields=['paypal_plan_id'])# Save the updated package with the PayPal plan ID
            return Response({'paypal_product_id': package_paypal_id,
                             'plan_response': plan_response}, status=status.HTTP_200_OK)
        
        except Package.DoesNotExist:
            return Response({'error': 'Package not found'}, status=status.HTTP_404_NOT_FOUND)
        


    def create_product_validity_day_plan(self, product_id, product_validity, access_token):
        """
        Create a product_validity-day recurring PayPal subscription plan
        """


        url = f"https://{PAYPAL_BASE_URL}/v1/billing/plans"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        payload = {
            "product_id": product_id,
            "name": f"{product_validity}-Day Recurring Plan",
            "description": f"Subscription renews every {product_validity} days",
            "status": "ACTIVE",
            "billing_cycles": [
                {
                    "frequency": {"interval_unit": "DAY", "interval_count": product_validity},
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,
                    "pricing_scheme": {"fixed_price": {"value": "10", "currency_code": "USD"}}
                }
            ],
            "payment_preferences": {
                "auto_bill_outstanding": True,
                "setup_fee": {"value": "0", "currency_code": "USD"},
                "setup_fee_failure_action": "CANCEL",
                "payment_failure_threshold": 1
            },
            "taxes": {"percentage": "0", "inclusive": False}
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"PayPal API error: {response.status_code} - {response.text}")
            return None
class Product(GenericAPIView):
    
    permission_classes = [IsAdminUserAuthenticated]
    
    def post(self, request):
        access_token = generate_access_token()
        print("Access Token:", access_token)  # Debugging line
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
        
        if product_details.paypal_product_id:
            return Response(f'Product already created on PayPal, Product ID: {product_details.paypal_product_id}', status=status.HTTP_208_ALREADY_REPORTED)

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
        print("Access Token:", access_token)  # Debugging line
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
        
class SubscriptionView(GenericAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        access_token = generate_access_token()
        print("Access Token:", access_token)  # Debugging line
        
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product_details = Package.objects.only('id', 'type',
                                                'paypal_product_id','validity', 
                                                'paypal_plan_id').get(id=product_id)

            if product_details.type == 'Free':
                return Response('Only Paid Products support for the subscription plan', status=status.HTTP_406_NOT_ACCEPTABLE)
        
            paypal_plan_id = product_details.paypal_plan_id
            product_price = product_details.price
            print("Package PayPal Plan ID:", paypal_plan_id)  # Debugging line
            if not paypal_plan_id:
                return Response({'error': 'No PayPal plan associated with this product'}, status=status.HTTP_404_NOT_FOUND) 
            subscription_response = self.create_subscription(paypal_plan_id, product_price, access_token)
            if not subscription_response:
                return Response({'error': 'Failed to create subscription on PayPal'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request):
        subscription_id = request.data.get('subscription_id')
        
        if not subscription_id:
            return Response(
                {'error': 'subscription_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Safely get the user instance
        user = get_object_or_404(User, id=request.user.id)

        try:
            user.paypal_subscription_id = subscription_id
            user.save(update_fields=['paypal_subscription_id'])
            print(f"Subscription ID saved for user: {user.username}")  # Debugging line

            return Response(
                {'message': 'Subscription ID saved successfully'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print(f"Error saving subscription ID for user {user.username}: {e}")
            return Response(
                {'error': 'Failed to save subscription ID'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def delete(self, request):
        user = get_object_or_404(User, id=request.user.id)
        access_token = generate_access_token()
        print("Access Token:", access_token)  # Debugging line
        try:
            subscription_response = self.cancel_subscription(user.paypal_subscription_id, access_token)
            user.paypal_subscription_id = None
            user.save(update_fields=['paypal_subscription_id'])
            print(f"Subscription ID removed for user: {user.username}")  # Debugging line
            return Response(
                {'message': 'Subscription ID removed successfully',
                 'Paypal_Response': subscription_response},
                
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print(f"Error removing subscription ID for user {user.username}: {e}")
            return Response(
                {'error': 'Failed to remove subscription ID'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def create_subscription(plan_id, product_price, access_token):
        """
        Create a PayPal subscription for the given plan ID
        """
        url = f'https://{PAYPAL_BASE_URL}/v1/billing/subscriptions'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'PayPal-Request-Id': 'SUBSCRIPTION-21092019-001',
            'Prefer': 'return=representation',
        }

        # Use current UTC time for start_time
        start_time = datetime.now(timezone.utc).isoformat()

        payload = {
            "plan_id": plan_id,
            "start_time": start_time,
            "quantity": "1",
            "shipping_amount": {"currency_code": "USD", "value": str(product_price)},
            "subscriber": {
                "name": {"given_name": "John", "surname": "Doe"},
                "email_address": "customer@example.com",
                "shipping_address": {
                    "name": {"full_name": "John Doe"},
                    "address": {
                        "address_line_1": "2211 N First Street",
                        "address_line_2": "Building 17",
                        "admin_area_2": "San Jose",
                        "admin_area_1": "CA",
                        "postal_code": "95131",
                        "country_code": "US"
                    }
                }
            },
            "application_context": {
                "brand_name": "walmart",
                "locale": "en-US",
                "shipping_preference": "SET_PROVIDED_ADDRESS",
                "user_action": "SUBSCRIBE_NOW",
                "payment_method": {
                    "payer_selected": "PAYPAL",
                    "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
                },
                "return_url": "https://example.com/returnUrl",
                "cancel_url": "https://example.com/cancelUrl"
            }
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code in [200, 201]:
            return response.json()  # Contains subscription ID, links, status, etc.
        else:
            print(f"PayPal API error {response.status_code}: {response.text}")
            return None
        
    def cancel_subscription(subscription_id, access_token, reason="Not satisfied with the service"):
        """
        Cancel a PayPal subscription
        """
        url = f'https://api-m.sandbox.paypal.com/v1/billing/subscriptions/{subscription_id}/cancel'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        payload = {"reason": reason}

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 204:
            # 204 No Content means the subscription was successfully canceled
            return {"status": "canceled"}
        else:
            return {"status": "error", "details": response.text}