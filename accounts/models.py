from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
# Create your models here.

class UserManager(BaseUserManager):
    
    def create_user(self, first_name, last_name, username, email, password =None):
        if not email:
            raise ValueError("user must have an email address")
        if not username:
            raise ValueError("user must have an username")

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,

        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
                                email=self.normalize_email(email),
                                username=username,
                                password=password,
                                first_name=first_name, 
                                last_name=last_name, 
                                )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using = self._db)
        return user
AUTH_PROVIDERS = {'facebook':'facebook', 'google':'google',
                  'twitter':'twitter', 'email':'email'}
class User(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    date_of_birth = models.DateField(default=None, null=True, blank=True)
    phone_number = models.CharField(max_length=50, default=None, null=True, blank=True)
    
    auth_provider = models.CharField(max_length=255, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))
     # Add a many-to-many field for interests
    interests = models.ManyToManyField('Interest', related_name='users', blank=True)
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    #required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD ='username'
    REQUIRED_FIELDS = ['first_name','last_name', 'email']


    objects = UserManager()

    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    def has_module_perms(self, add_label):
        return True
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }

def user_profile_picture_upload_path(instance, filename):
    # Generate the upload path based on the user's ID
    return f'users/{instance.user.username}/profile_pictures/{filename}'

def user_cover_photo_upload_path(instance, filename):
    # Generate the upload path based on the user's ID
    return f'users/{instance.user_profile.user.username}/cover_photos/{filename}'


class UserProfile(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to=user_profile_picture_upload_path ,blank=True,null=True)
    
    # cover_photo = models.ManyToManyField('CoverPhoto', related_name='user_profiles', blank=True)
    
    family_plan = models.ForeignKey("FamilyPlanChoice", on_delete=models.SET_NULL, blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)  # Add the 'height' field here
    drink = models.ForeignKey("DrinkChoice", on_delete=models.SET_NULL, blank=True, null=True)
    religion = models.ForeignKey("Religion", on_delete=models.SET_NULL, blank=True, null=True)
    education = models.ForeignKey("EducationType", on_delete=models.SET_NULL, blank=True, null=True)
    relationship_goals = models.ForeignKey("RelationShipGoal", on_delete=models.SET_NULL, blank=True, null=True)
    workout = models.ForeignKey("Workout", on_delete=models.SET_NULL, blank=True, null=True)
    smoke = models.ForeignKey("SmokeChoice", on_delete=models.SET_NULL, blank=True, null=True)
    languages = models.ManyToManyField('Language', related_name='users', blank=True)
 
    address_line1 = models.CharField(max_length=50, blank=True, null=True)
    address_line2 = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
class ProfilePreference(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True)
    family_choices = models.ManyToManyField('FamilyPlanChoice', related_name='profile_preferences_family', blank=True)
    drink_choices = models.ManyToManyField('DrinkChoice', related_name='profile_preferences_drink', blank=True)
    religion_choices = models.ManyToManyField('Religion', related_name='profile_preferences_religion', blank=True)
    education_choices = models.ManyToManyField('EducationType', related_name='profile_preferences_education', blank=True)
    relationship_choices = models.ManyToManyField('RelationShipGoal', related_name='profile_preferences_relationship', blank=True)
    workout_choices = models.ManyToManyField('Workout', related_name='profile_preferences_workout', blank=True)
    smoke_choices = models.ManyToManyField('SmokeChoice', related_name='profile_preferences_smoke', blank=True)
    languages_choices =  models.ManyToManyField('Language', related_name='profile_preferences_languages', blank=True)

class CoverPhoto(models.Model):
    

    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True,  related_name='cover_photos')
    image = models.ImageField(upload_to=user_cover_photo_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user_profile.user.username)
    
class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class DrinkChoice(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
class FamilyPlanChoice(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Workout(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Religion(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class RelationShipGoal(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class SmokeChoice(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
class EducationType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

