from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User, UserProfile

    
class Favorite(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='favorites')
    favored_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='favorited_by')

    def __str__(self):
        return f"{self.user.user.username} has favorited {self.favored_by.user.username}"

class Like(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='like')
    liked_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='liked_by')

class BlockedUser(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='blocked_user')
    blocked_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='blocked_by')