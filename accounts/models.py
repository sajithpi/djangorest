from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
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

class User(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)

    #required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD ='email'
    REQUIRED_FIELDS = ['username','first_name','last_name']


    objects = UserManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    def has_module_perms(self, add_label):
        return True


def user_profile_picture_upload_path(instance, filename):
    # Generate the upload path based on the user's ID
    return f'users/{instance.user.id}/profile_pictures/{filename}'

def user_cover_photo_upload_path(instance, filename):
    # Generate the upload path based on the user's ID
    return f'users/{instance.user_profile.user.id}/cover_photos/{filename}'


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to=user_profile_picture_upload_path ,blank=True,null=True)
    # cover_photo = models.ManyToManyField('CoverPhoto', related_name='user_profiles', blank=True)
   
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

class CoverPhoto(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True,  related_name='cover_photos')
    image = models.ImageField(upload_to=user_cover_photo_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)