from rest_framework import generics, serializers
from rest_framework.response import Response
from rest_framework import status
from .models import Sticker


class StickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sticker
        fields = '__all__'
