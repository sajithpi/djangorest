from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import json
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
    showAge = models.BooleanField(default=True)
    showDistance  = models.BooleanField(default=False)
    auth_provider = models.CharField(max_length=255, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))
    register_otp = models.CharField(max_length=6, null=True, blank=True)
  
    # Add a many-to-many field for interests
    interests = models.ManyToManyField('Interest', related_name='users', blank=True)
    
    # Add sponsor field as a foreign key to the same User model
    sponsor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sponsored_users')
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('TM', 'Transgender Male'),
        ('TF','Transgender Female'),
    )
    ORIENTATION_CHOICES = (
        ('Hetero', 'Heterosexual'),
        ('Homo', 'Homo'),
        ('Pan', 'Pansexual'),
        ('Bi','Bisexual'),
    )
    MLM_CHOICES = (
        ('inactive', 'inactive'),
        ('active', 'active'),
    )
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, null=True, blank=True)
    orientation = models.CharField(max_length=7, choices=ORIENTATION_CHOICES, null=True, blank=True)
    mlm_status = models.CharField(max_length=8, choices=MLM_CHOICES, default = 'inactive', null=True, blank=True)
    #required
    package = models.ForeignKey("Package", on_delete=models.SET_NULL, blank=True, null=True)
    package_validity =  models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank = True, null = True)
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    login_status = models.BooleanField(default=False)
    has_2fa_passed = models.BooleanField(default=False)
    has_2fa_enabled = models.BooleanField(default=False)
    login_otp = models.CharField(max_length=7, blank=True, null=True)
    login_otp_validity = models.DateTimeField(blank=True, null=True)

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

def package_upload_path(instance, filename):
    return f'packages/{instance.name}/{filename}'

def kyc_upload_path(instance, filename):
    print(f"KYC:{instance}")
    return f'kyc/{instance.user_profile.user.username}/{filename}'

class Package(models.Model):
    
    PACKAGE_CHOICES = (
        ('Free', 'Free'),
        ('Paid', 'Paid'),
    )
    
    name = models.CharField(max_length=50, blank=True, null=True)
    package_img = models.ImageField(upload_to=package_upload_path, blank=True, null=True)
    features = models.TextField(blank=True, null=True)
    price = models.FloatField(default=0)
    type = models.CharField(max_length=10, choices=PACKAGE_CHOICES, blank=True, null=True)
    validity = models.FloatField(default=1)

    # def set_features(self, features):
    #     self.features = json.dumps(features)

    # def get_features(self):
    #     return json.loads(self.features) if self.features else []

    # features_list = property(get_features, set_features)
    
class Order(models.Model):
    
    STATUS_CHOICES = (
        (0, 'Initiated'),  # Order initiated
        (1, 'Success'),    # Order successfully completed
        (2, 'Failed'),     # Order failed
    )
    user_id = models.ForeignKey("UserProfile", on_delete = models.CASCADE, blank = True, null = True)
    order_id = models.CharField(max_length = 100, blank = True, null = True)
    package_id = models.ForeignKey(Package, on_delete =models.SET_NULL, blank = True, null = True)
    price = models.CharField(max_length=10, default=None, null=True, blank=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
class UserProfile(models.Model):
    
   
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to=user_profile_picture_upload_path ,blank=True,null=True)
    
    # cover_photo = models.ManyToManyField('CoverPhoto', related_name='user_profiles', blank=True)
    about_me = models.CharField(max_length=1000, blank=True, null=True)
    family_plan = models.ForeignKey("FamilyPlanChoice", on_delete=models.SET_NULL, blank=True, null=True)
    height= models.FloatField(blank=True, null=True, verbose_name='Height in cm')
    drink = models.ForeignKey("DrinkChoice", on_delete=models.SET_NULL, blank=True, null=True, related_name='drink_choice')
    religion = models.ForeignKey("Religion", on_delete=models.SET_NULL, blank=True, null=True)
    education = models.ForeignKey("EducationType", on_delete=models.SET_NULL, blank=True, null=True)
    relationship_goals = models.ForeignKey("RelationShipGoal", on_delete=models.SET_NULL, blank=True, null=True)
    workout = models.ForeignKey("Workout", on_delete=models.SET_NULL, blank=True, null=True)
    smoke = models.ForeignKey("SmokeChoice", on_delete=models.SET_NULL, blank=True, null=True)
    languages = models.ManyToManyField('Language', related_name='users', blank=True)
    company = models.CharField(max_length=50, blank=True, null=True)
    job_title = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    is_edited = models.BooleanField(default=False)
    city = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, )
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        # Set modified_at to current time in the timezone specified in settings
        self.modified_at = settings.NOW
        super().save(*args, **kwargs)


class KycCategory(models.Model):
    name = models.CharField(max_length = 100, blank = True)
    

class KycDocument(models.Model):
    STATUS_CHOICES = (
        (0, 'Pending'),  # KYC Pending
        (1, 'Approved'),  # KYC Approved
        (2, 'Rejected'),  # KYC Rejected
    )

    user_profile = models.ForeignKey(UserProfile, related_name='kyc_documents', on_delete=models.CASCADE)
    document = models.ImageField(upload_to=kyc_upload_path, blank=True, null=True)
    type = models.ForeignKey(KycCategory, related_name='kyc_category', on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    
    
class Notification(models.Model):
    
    from_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True, related_name='from_user')
    to_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True, related_name='to_user')
    type = models.CharField(max_length=10, blank=True, null=True)
    description = models.CharField(max_length=75, blank=True, null=True)
    user_has_seen = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

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
    
class UserTestimonial(models.Model):
    
    STATUS_CHOICES = (
        (0,0), #pending
        (1,1), #accepted
        (2,2), #rejected
    )
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True, related_name='user_testimonial')
    description = models.CharField(max_length=500, blank=False, null=False)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)
    
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

class Orientation(models.Model):
    name = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name
    
class EmailTemplate(models.Model):
    TEMPLATE_CHOICE = (
        ('register', 'register'),
        ('otp', 'otp'), 
        ('reset_password','reset_password')
    )
    subject = models.CharField(max_length=255)
    content = models.TextField()
    type =  models.CharField(max_length=25, choices=TEMPLATE_CHOICE, null=True, blank=True)

    def __str__(self):
        return self.subject

