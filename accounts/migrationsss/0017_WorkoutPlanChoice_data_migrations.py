from django.db import migrations
from ..models import Workout

WORKOUT_CHOICES = [
    "Everyday",
    "Often",
    "Sometimes",
    "Never",
]

def addWorkoutChoices(apps, schema_editor):
  
    for choice in WORKOUT_CHOICES:
        Workout.objects.get_or_create(name=choice)

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0014_drinkchoice_educationtypes_familyplanchoice_and_more'),  # Include the correct previous migration
    ]

    operations = [
        migrations.RunPython(addWorkoutChoices)
    ]