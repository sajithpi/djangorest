from rest_framework import serializers
from .models import Favorite, Rating
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
        
class RatingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Rating
        fields = ['user', 'cover_photo', 'rated_by', 'rate_count']
        def create(self, validated_data):
            
            user = self.context['user']
            rated_by = self.context['rated_by']
            cover_photo = self.context['cover_photo']
            rate_count = validated_data['rate_count']
            print(f"user{user} rated_by:{rated_by} cover_photo:{cover_photo} rate_count:{rate_count}")
            print(f"validate data:{validated_data}")
            # Your custom create logic here
            rating = Rating.objects.create(user = user, rated_by = rated_by, cover_photo = cover_photo, rate_count = rate_count)
            return rating