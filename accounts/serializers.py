from rest_framework import serializers
from .models import User

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
    

    
