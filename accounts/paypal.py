from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from paypalrestsdk import Payment, Payout, Api
from django.conf import settings
from . models import Order, User, UserProfile, Package
import requests
import json
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.utils import timezone

PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
PAYPAL_CLIENT_SECRET = settings.PAYPAL_CLIENT_SECRET
PAYPAL_BASE_URL = settings.PAYPAL_BASE_URL

def generate_access_token():
    client_id = PAYPAL_CLIENT_ID
    client_secret = PAYPAL_CLIENT_SECRET
    token_url = f'https://{PAYPAL_BASE_URL}/v1/oauth2/token'  # Replace with the production URL for live mode

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {
        'grant_type': 'client_credentials',
    }

    response = requests.post(token_url, headers=headers, auth=(client_id, client_secret), data=data)

    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        # Handle error response
        print(response.text)
        return None
    
class PayPalPaymentView(APIView):
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'price': openapi.Schema(type=openapi.TYPE_NUMBER, description='The price of the product'),
                'product_id': openapi.Schema(type=openapi.TYPE_STRING, description='The ID of the product'),
            },
            required=['price', 'product_id']
        ),
        responses={
            200: openapi.Response('Successful payment response'),
            400: openapi.Response('Bad Request'),
            500: openapi.Response('Internal Server Error'),
        },
        tags=['Paypal']
    )
    def post(self, request, *args, **kwargs):
        try:
            # Extract price and product_id from the request data
            price = float(request.data.get('price'))
            product_id = request.data.get('product_id')

            # Generate access token (replace with your own logic)
            access_token = generate_access_token()

            # Create the PayPal order
            url = f'https://{PAYPAL_BASE_URL}/v2/checkout/orders'  # Replace with the production URL for live mode
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            payload = {
                'intent': 'CAPTURE',
                'purchase_units': [
                    {
                        'amount': {
                            'currency_code': 'USD',
                            'value': price,  # Replace with the actual total value
                        },
                    },
                ],
            }

            # Make the PayPal API request to create an order
            response = requests.post(url, headers=headers, json=payload)

            # Check if the PayPal API request was successful (status code 201)
            if response.status_code == 201:
                # Extract the order ID from the PayPal API response
                paypal_order_id = response.json().get('id')

                # Fetch user and user profile
                user = User.objects.get(username=request.user)
                user_profile = UserProfile.objects.get(user=user)

                # Fetch the package based on the product_id
                package_id = Package.objects.get(id=product_id)

                # Create an order object and save it to the database
                order = Order(user_id=user_profile, order_id=paypal_order_id, package_id=package_id, price=price, status=0)
                order.save()

                # Return a JSON response with the PayPal API response
                return JsonResponse(response.json(), safe=False)
            else:
                # If the PayPal API request was not successful, return an error response
                return Response({'error': 'Failed to create PayPal order'}, status=response.status_code)
        except ValueError as e:
            # Handle JSON decoding error
            print(f"Error decoding JSON response: {e}")
            return Response({'error': 'Error decoding JSON response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CaptureOrderView(APIView):
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'order_id': openapi.Schema(type=openapi.TYPE_STRING, description='The ID of the order to capture'),
            },
            required=['order_id']
        ),
        responses={
            200: openapi.Response('Successful capture response'),
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Order not found'),
            500: openapi.Response('Internal Server Error'),
        },
        tags=['Paypal']
    )
    def post(self, request):
        try:
            # Assuming order_id is part of the request data
            order_id = request.data.get('order_id')

            # Fetch the order from the database using the order_id
            order = Order.objects.get(order_id=order_id)

            # Generate access token (replace with your own logic)
            access_token = generate_access_token()

            if access_token:
                # Capture the PayPal order
                url = f'https://{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture'  # Replace with the production URL for live mode
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {access_token}',
                }

                response = requests.post(url, headers=headers)
                response.raise_for_status()  # Raise an exception for HTTP errors (status code 4xx or 5xx)

                # Check if the PayPal order status is COMPLETED
                if response.json().get('status') == 'COMPLETED':
                    print(f"Payment for order ID {order_id} is COMPLETED")
                    order.status = OrderStatus.COMPLETED  # Assuming 1 represents a completed order status
                    order.save()

                    # Update user package validity
                    package_id = order.package_id.id
                    package_data = Package.objects.get(id=package_id)
                    user_package_validity = timezone.now() + relativedelta(months=package_data.validity)
                    print(f"user_package_validity for order ID {order_id}: {user_package_validity}")
                    user = User.objects.get(username =request.user)
                    user.package = package_data
                    user.package_validity = user_package_validity
                    user.mlm_status = 'upgraded'
                    user.save()

                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                # Handle the case where obtaining the access token fails
                order.status = OrderStatus.FAILED  # Assuming 2 represents a failed order status
                order.save()
                print("Failed to obtain access token")
                return Response({"error": "Failed to obtain access token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.exceptions.RequestException as e:
            print(f"Error while capturing PayPal order: {e}")
            # Handle request exception (e.g., network issues, connection error)
            order.status = OrderStatus.FAILED  # Assuming 2 represents a failed order status
            order.save()
            return Response({"error": f"Failed to capture PayPal order: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Order.DoesNotExist:
            print(f"Order with ID {order_id} does not exist")
            return Response({"error": f"Order with ID {order_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            # Handle JSON decoding e
            print(f"Error decoding JSON response: {e}")
            order.status = OrderStatus.FAILED  # Assuming 2 represents a failed order status
            order.save()
            return Response({"error": "Error decoding JSON response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# Constants representing order status
class OrderStatus:
    COMPLETED = 1
    FAILED = 2