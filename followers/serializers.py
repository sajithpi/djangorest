from rest_framework import serializers
from .models import Follower
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http  import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.exceptions import AuthenticationFailed

class FollowSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Follower
        fields = ['followed_by', 'following']

        def create(self, validate_data):
            print(f"validate data:{validate_data}")
            follow_Data = Follower.objects.create(followed_by=validate_data['followed_by'],
                                                  following=validate_data['following'])
            follow_Data.save()
            return follow_Data