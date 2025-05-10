from google.auth.transport import requests
from google.oauth2 import id_token
import requests


class Google:
    """Google class to fetch the user info and return it"""
    
    def generate_id_token(access_token):

        # Replace this with your access token
        # access_token = "ya29.a0AfB_byDwplGwYipBJThfng5t7kU-Kqo6XiJItuSPuago7916u18krjOF34dktPfXrHG0kDMzMfe6ZkBLAE59FijB4FLpmf4XfSuma3W800oPiWPvAX2UZPV5TrUsgWP9QvlC2KYlIQ-Ww_IHnfzdnsY8qcmrF1EV0waCgYKAd0SAQ4SFQGOcNnCJBLQwYrz05VoyYaMqVJ3tA0169"

        # Define the API endpoint
        api_url = "https://www.googleapis.com/oauth2/v3/userinfo"

        # Include the access token in the query parameters
        params = {
            "access_token": access_token
        }

        # Make the API request
        response = requests.get(api_url, params=params)

        # Check if the request was successful
        
        if response.status_code == 200:
            user_info = response.json()
            return user_info
        else:
            message = f"API request failed with status code: {response.status_code}"
            print(message)
            return 0

    

    @staticmethod
    def validate(auth_token):
        
        """
        validate method Queries and Google oAUTH2 api to fetch the user info
        
        
        """
        try:
            idinfo = id_token.verify_oauth2_token(auth_token, requests.Request())

            if 'accounts.google.com' in idinfo['iss']:
                return idinfo
        except:
            return "The token is invalid or expired"