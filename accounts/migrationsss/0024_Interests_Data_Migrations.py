from django.db import migrations
from ..models import  Interest

INTEREST_CHOICES = [
    "Coding",
    "Dance",
    "Singing",
    "Travel",
    "Reading",
    "Sports",
    "Art"
]

def addInterestChoices(apps, schema_editor):
  
    for choice in INTEREST_CHOICES:
        Interest.objects.get_or_create(name=choice)

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0012_interest'),  # Include the correct previous migration
    ]

    operations = [
        migrations.RunPython(addInterestChoices)
    ]