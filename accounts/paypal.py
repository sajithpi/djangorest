from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from paypalrestsdk import Payment, Payout, Api
from django.conf import settings
import requests
import json
from django.http import JsonResponse

PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
PAYPAL_CLIENT_SECRET = settings.PAYPAL_CLIENT_SECRET


def generate_access_token():
    client_id = PAYPAL_CLIENT_ID
    client_secret = PAYPAL_CLIENT_SECRET
    token_url = 'https://api.sandbox.paypal.com/v1/oauth2/token'  # Replace with the production URL for live mode

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
       def post(self, request, *args, **kwargs):
        # Get cart information from the frontend
        # cart = json.loads(request.body)
        
        # Generate access token (replace with your own logic)
        access_token = generate_access_token()

        # Create the PayPal order
        url = 'https://api.sandbox.paypal.com/v2/checkout/orders'  # Replace with the production URL for live mode
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
                        'value': '100.00',  # Replace with the actual total value
                    },
                },
            ],
        }

        response = requests.post(url, headers=headers, json=payload)
        return JsonResponse(response.json(), safe=False)
    
class CaptureOrderView(APIView):
    def post(self, request):
        order_id = request.data.get('order_id')  # Assuming order_id is part of the URL parameters

        try:
            # Generate access token (replace with your own logic)
            access_token = generate_access_token()

            if access_token:
                # Capture the PayPal order
                url = f'https://api.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture'  # Replace with the production URL for live mode
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {access_token}',
                }

                response = requests.post(url, headers=headers)
                response.raise_for_status()  # Raise an exception for HTTP errors (status code 4xx or 5xx)
                # Check if the PayPal order status is COMPLETED
                if response.json().get('status') == 'COMPLETED':
                    print(f"PAYMENT IS COMPLETED")
                

                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to obtain access token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.exceptions.RequestException as e:
            # Handle request exception (e.g., network issues, connection error)
            print(f"Error while capturing PayPal order: {e}")
            return Response({"error": "Failed to capture PayPal order"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValueError as e:
            # Handle JSON decoding error
            print(f"Error decoding JSON response: {e}")
            return Response({"error": "Error decoding JSON response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)