from django.db import migrations
from ..models import TravelAim

TravelAims_List = [
    "Honeymoon Planning Partner",
    "Adventure and Romance",
    "Foodie Date Companion",
    "Outdoor Date Enthusiast",
    "Museum and Art Date",
    "Travel and Love Connection",
    "Festival Date and Romance",
    "Nature's Love Haven",
]

def addTravelAimChoices(apps, schema_editor):
  
    for choice in TravelAims_List:
        TravelAim.objects.get_or_create(name=choice)

class Migration(migrations.Migration):
    dependencies = [
        ('travel', '0001_initial'),  # Include the correct previous migration
    ]

    operations = [
        migrations.RunPython(addTravelAimChoices)
    ]