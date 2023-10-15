from rest_framework import serializers
from .models import Favorite
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http  import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.exceptions import AuthenticationFailed

class FavoriteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Favorite
        fields = ['favored_by']

        def create(self, validate_data):
            print(f"validate data:{validate_data}")
            user = self.context['user']
            favorite_data = Favorite.objects.create(user=user,
                                                  favored_by=validate_data['favored_by'])
            favorite_data.save()
            return favorite_data