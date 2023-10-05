from django.db import migrations
from ..models import  SmokeChoices

SMOKE_CHOICES = [
    "Socially",
    "Never",
    "Regularly",
    "Skip",
]

def addSmokeChoices(apps, schema_editor):
  
    for choice in SMOKE_CHOICES:
        SmokeChoices.objects.get_or_create(name=choice)

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0014_drinkchoice_educationtypes_familyplanchoice_and_more'),  # Include the correct previous migration
    ]

    operations = [
        migrations.RunPython(addSmokeChoices)
    ]