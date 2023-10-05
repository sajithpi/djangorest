from django.db import migrations
from ..models import  EducationTypes

EDUCATION_CHOICES = [
    "High School",
    "Trade/Tech School",
    "In collage",
    "Undergraduate degree",
    "Graduate degree",
    "Skip"
]

def addEducationChoices(apps, schema_editor):
  
    for choice in EDUCATION_CHOICES:
        EducationTypes.objects.get_or_create(name=choice)

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0014_drinkchoice_educationtypes_familyplanchoice_and_more'),  # Include the correct previous migration
    ]

    operations = [
        migrations.RunPython(addEducationChoices)
    ]