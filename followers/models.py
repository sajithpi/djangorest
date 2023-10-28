from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User, UserProfile, CoverPhoto

    
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

class Poke(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='poke')
    poked_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='poked_by')
    
class Rating(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='rating_user')
    cover_photo = models.ForeignKey(CoverPhoto, on_delete=models.CASCADE, related_name='cover_photo')
    rated_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='rated_by')
    rate_count = models.PositiveIntegerField(default=0)