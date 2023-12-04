from rest_framework import serializers
from . import google, facebook
from .register import register_social_user
from rest_framework.response import Response
from rest_framework import status
import json


GOOGLE_CLIENT_ID = '74750236370-melid0v5g6l1t2kt9la69eigjafq68qi.apps.googleusercontent.com'

class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()
    
    # New field to accept the 'device' variable

    def validate_auth_token(self, auth_token):
        
        
        # auth_token = "ya29.a0AfB_byA_SWulbewEdWNC6o77sguj5YEz8hlKcZqB20X3IE8gQelw0U7ri5HEiU77xgVUKdcUTtxky5Ja0rncWEBQIsS_J-ACjybZaznDjyPBMoiZBNDOSRSLmgfUyN9blWOZjEIKYtFLqUwsULKqxeqYi5ICwyPBUAaCgYKARsSAQ4SFQGOcNnCMu"
        # user_data = google.Google.validate(auth_token)
        device = self.context['device']
        print(f"GMAIL DEVICE:{device}")
        if device == 'web':
            user_data = google.Google.generate_id_token(auth_token)
            try:
                user_data['sub']
            except Exception as e:
                raise serializers.ValidationError(
                    'The token is invalid or expired, please login again,'
                )
        else:
           user_data = json.loads(auth_token)
        if isinstance(user_data, dict):
            user_id = user_data.get('name')
            if user_id is not None:
                print(f"USER ID:{user_id}")
        else:
            print("Unexpected user_data type:", type(user_data))
        
        # if user_data['aud'] != GOOGLE_CLIENT_ID:
        #     raise AuthenticationFailed('Oops, who are you?')
        
        print(f"USER ID:{user_data['name']}")
        
        user_id = user_data['sub'] if device == 'web' else user_data['id']
        email = user_data['email']
        name = user_data['name']
        provider = 'google'

        return register_social_user(provider = provider, user_id = user_id, email = email, name = name)
    
class FacebookSocialAuthSerializer(serializers.Serializer):
    """Handles seriallization of facebook related data"""
    auth_token = serializers.CharField()
    def validate_auth_token(self, auth_token):
        # user_data = facebook.Facebook.validate(auth_token)
        # print(f"user_Data:{user_data}")
        print(f"auth_token:{auth_token}")
        try:
            user_id = auth_token['userID']
            email = auth_token['email']
            name = auth_token['name']
            provider = 'facebook'
            return register_social_user(
                provider=provider,
                user_id=user_id, 
                email=email, 
                name=name,
            )
        except Exception as e:
            raise serializers.ValidationError('The token is invalid or expired. please login again')