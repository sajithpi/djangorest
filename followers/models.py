from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User, UserProfile

# class Follower(models.Model):
#     follower = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='follower')
#     following = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='following')

#     def __str__(self):
#         return f"{self.follower.user.username} is following {self.following.user.username}"
    
class Favorite(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='favorites')
    favored_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='favorited_by')

    def __str__(self):
        return f"{self.user.user.username} has favorited {self.favored_by.user.username}"
