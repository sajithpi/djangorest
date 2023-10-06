from django.db import migrations
from ..models import  Language

LANGUAGE_CHOICES = [
    "Spanish",
    "Chinese",
    "Tagalog",
    "Vietnamese",
    "French",
    "German",
    "Arabic",
    "Russian",
    "Korean",
    "Italian",
    "English",

    
]

def addLanguageChoices(apps, schema_editor):
  
    for choice in LANGUAGE_CHOICES:
        Language.objects.get_or_create(name=choice)

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0026_language_userprofile_languages'),  # Include the correct previous migration
    ]

    operations = [
        migrations.RunPython(addLanguageChoices)
    ]