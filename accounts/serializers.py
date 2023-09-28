from rest_framework import serializers
from .models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http  import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.exceptions import AuthenticationFailed

class UserSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["id","email","username","password","first_name","last_name"]

    def create(self, validate_data):
        user = User.objects.create(email=validate_data['email'],
                                       username=validate_data['username'],
                                       first_name=validate_data['first_name'],
                                       last_name=validate_data['last_name'])
        user.set_password(validate_data['password'])
        user.save()
        return user
    
class ResetPasswordEmailSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['email']

        
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password','token','uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)