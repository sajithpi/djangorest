from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User, UserProfile

class Follower(models.Model):
    followed_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='followed_by')
    following = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='following')

    def __str__(self):
        return f"{self.followed_by.user.username} is following {self.following.user.username}"