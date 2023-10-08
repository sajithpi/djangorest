from rest_framework import serializers
from . import google, facebook
from .register import register_social_user



GOOGLE_CLIENT_ID = '74750236370-melid0v5g6l1t2kt9la69eigjafq68qi.apps.googleusercontent.com'

class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        print(f"user data:{user_data}")
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'The token is invalid or expired, please login again,'
            )
        # if user_data['aud'] != GOOGLE_CLIENT_ID:
        #     raise AuthenticationFailed('Oops, who are you?')
        
        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']
        provider = 'google'

        return register_social_user(provider = provider, user_id = user_id, email = email, name = name)
    
class FacebookSocialAuthSerializer(serializers.Serializer):
    """Handles seriallization of facebook related data"""
    auth_token = serializers.CharField()
    def validate_auth_token(self, auth_token):
        user_data = facebook.Facebook.validate(auth_token)
        print(f"user_Data:{user_data}")
        try:
            user_id = user_data['id']
            email = user_data['email']
            name = user_data['name']
            provider = 'facebook'
            return register_social_user(
                provider=provider,
                user_id=user_id, 
                email=email, 
                name=name,
            )
        except Exception as e:
            raise serializers.ValidationError('The token is invalid or expired. please login again')