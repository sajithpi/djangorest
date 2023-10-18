from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, UserProfile, CoverPhoto, Interest, ProfilePreference, Notification, Language, FamilyPlanChoice, EducationType, DrinkChoice, Workout, SmokeChoice, RelationShipGoal, Religion
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http  import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.exceptions import AuthenticationFailed
from . otp import send_otp_via_mail

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        # Add custom data to the response
        _2fa = user.has_2fa_enabled
        if _2fa == True:
            send_otp_via_mail(user.email, 'login')
            
        print(f"2fa status:{_2fa}")
        data['has_2fa_enabled'] = _2fa
        return data
    
class UserSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["id","email","username","password","first_name","last_name","gender","orientation","date_of_birth","showAge","showDistance","phone_number",]

    def create(self, validated_data):
        user = User.objects.create(email=validated_data['email'],
                                       username=validated_data['username'],
                                       first_name=validated_data['first_name'],
                                       last_name=validated_data['last_name'],
                                       gender = validated_data["gender"],
                                       orientation = validated_data["orientation"],
                                       phone_number = validated_data.get('phone_number'),
                                       date_of_birth = validated_data.get('date_of_birth'),)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","email","username","password","first_name","last_name","gender","orientation","date_of_birth","showAge","showDistance","phone_number",]  # Add other user fields as needed

class UpdateUserProfileSerializer(serializers.ModelSerializer):
    
    cover_photos = serializers.ListField(child = serializers.ImageField(), required = False)
    # languages = serializers.ListField(
    #             child = serializers.DictField(
    #                 child = serializers.CharField(max_length=100),
    #             ),
    #             required = False
    #             )
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture',
            'family_plan',
            'height',
            'drink',
            'religion',
            'education',
            'relationship_goals',
            'workout',
            'smoke',
            # 'languages',
            'cover_photos',
             
            'company',
            'job_title',
            'country',
            'is_edited',
            'city',
            'pin_code',
            
        ]
    def update(self, instance, validated_data):
        cover_photos_data = validated_data.pop('cover_photos',[])
        # Update specific fields in the UserProfile model
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Create CoverPhoto objects and associate them with the user's UserProfile
        # Process cover photos data
        for image_data in cover_photos_data:
            CoverPhoto.objects.create(user_profile=instance, image=image_data)
            
        return instance
    
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
    
class CoverPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverPhoto
        fields = '__all__'
        
class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'
    
class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id','name']

        
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializers()
    # languages = serializers.CharField(source='languages.name', many = True, read_only=True)
    languages = LanguageSerializer(many = True)
    cover_photos = CoverPhotoSerializer(many=True)  # Use 'cover_photos' (plural) here
    height = serializers.SerializerMethodField()
    # def get_drink_name(self, obj):
        # return obj.drink.drinkchoice.name

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'profile_picture',
            'cover_photos',  # Use 'cover_photos' (plural) here
            'family_plan',
            'drink',
            'religion',
            'height',
            'education',
            'relationship_goals',
            'workout',
            'smoke',
            'languages',
            'company',
            'job_title',
            'interests',
            'country',
            'is_edited',
            'city',
            'pin_code',
            'created_at',
            'modified_at',
        ]
        
    # Add a SerializerMethodField to include the user's interests
    interests = serializers.SerializerMethodField()
    languages = serializers.SerializerMethodField()
    
    def get_interests(self, obj):
         # Access the user's interests through the UserProfile's user field
        return [interest.name for interest in obj.user.interests.all()]
    
    def get_languages(self, obj):
        
        return [{'label':languages.name, 'value':languages.name} for languages in obj.languages.all()]
    
    def get_height(self, obj):
        feet = inches = 0
        # Calculate the total inches
        if obj.height:
            total_inches = float(obj.height) / 2.54
            # Calculate the number of feet
            feet = int(total_inches//12)
            # Calculate the remaining inches
            inches = int(total_inches % 12) 
        
        return {'cm':obj.height , 'feet':feet, 'inches':inches}

class UploadCoverPhotoSerializer(serializers.ModelSerializer):
    
    cover_photos = serializers.ListField(child = serializers.ImageField(), required = False)

    class Meta:
        model = CoverPhoto
        fields = [
            'cover_photos',
        ]
    def update(self, instance, validated_data):
        cover_photos_data = validated_data.pop('cover_photos',[])
        # Update specific fields in the UserProfile model
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Create CoverPhoto objects and associate them with the user's UserProfile
        # Process cover photos data
        for image_data in cover_photos_data:
            CoverPhoto.objects.create(user_profile=instance, image=image_data)
            
        return instance
    
class CombinedSerializer(serializers.Serializer):
    data_a = UpdateUserSerializer()  # Use your serializer for data A
    data_b = UpdateUserProfileSerializer()  # Use another serializer for data B

class ProfilePreferenceSerializer(serializers.ModelSerializer):
    family_choices = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=FamilyPlanChoice.objects.all()
    )
    drink_choices = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=DrinkChoice.objects.all()
    )
    religion_choices = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Religion.objects.all()
    )
    education_choices = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=EducationType.objects.all()
    )
    relationship_choices = serializers.SlugRelatedField(
        many =True,
        slug_field='name',
        queryset=RelationShipGoal.objects.all()
    )
    workout_choices = serializers.SlugRelatedField(
        many = True,
        slug_field='name',
        queryset=Workout.objects.all()
    )
    smoke_choices = serializers.SlugRelatedField(
        many = True,
        slug_field='name',
        queryset=SmokeChoice.objects.all()
    )
    languages_choices = serializers.SlugRelatedField(
        many = True,
        slug_field='name',
        queryset=Language.objects.all()
    )
    class Meta:
        model = ProfilePreference
        fields = '__all__'

        

class NotificationSerializer(serializers.ModelSerializer):
    from_user = serializers.CharField(source='from_user.user.username', read_only=True)
    to_user = serializers.CharField(source='to_user.user.username', read_only=True)

    class Meta:
        model = Notification
        fields = ['from_user', 'to_user', 'type', 'description', 'user_has_seen', 'date_added']