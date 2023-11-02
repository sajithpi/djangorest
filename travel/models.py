from django.db import models
from accounts.models import User, UserProfile
# Create your models here.

# class TravelPlan(models.Model):
   
#     TRAVEL_CHOICES = (
#         ('INITIATED', 'INITIATED'),
#         ('COMPLETED', 'COMPLETED'),
#         ('CANCELED', 'CANCELED'),
#         ('PENDING', 'PENDING')
#     )
#     user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True)
#     latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
#     longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
#     # looking_for = models.ForeignKey("LookingFor", on_delete=models.SET_NULL, blank=True, null=True)
#     # type = models.ForeignKey("Type", on_delete=models.SET_NULL, blank=True, null=True)
#     travel_date = models.DateTimeField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     modified_at = models.DateTimeField(auto_now=True)
#     status = models.CharField(max_length=11, choices=TRAVEL_CHOICES, null=True, blank=True)
    
class TravelType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class TravelAim(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    