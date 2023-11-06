from django.db import models
from accounts.models import User, UserProfile
# Create your models here.

class MyTrip(models.Model):
   
    TRAVEL_CHOICES = (
        ('planning', 'planning'),
        ('completed', 'completed'),
        ('canceled', 'canceled'),
        ('pending', 'pending')
    )
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location = models.CharField(max_length=50, null=True, blank=True)
    # looking_for = models.ForeignKey("LookingFor", on_delete=models.SET_NULL, blank=True, null=True)
    # type = models.ForeignKey("Type", on_delete=models.SET_NULL, blank=True, null=True)
    # intrested_users = models.ManyToManyField(UserProfile, related_name='Interested_user', blank=True)
    travel_date = models.DateTimeField(blank=True, null=True)
    days = models.PositiveIntegerField(blank=True, null=True)
    description = models.CharField(max_length=2500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=11, choices=TRAVEL_CHOICES, default='planning', null=True, blank=True)
    
class TravelType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class TravelAim(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    

class TravelRequest(models.Model):

    TRIP_REQUEST_CHOICES = (
        (0,'PENDING'),
        (1,'ACCEPTED'),
        (2,'REJECTED')
    )    
 
    trip = models.ForeignKey(MyTrip, on_delete=models.CASCADE, blank=False, null=False)
    requested_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=False, null=False)
    description = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=1, default=0, choices=TRIP_REQUEST_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)