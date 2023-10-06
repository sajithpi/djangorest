from django.db import migrations
from ..models import Religion

RELIGIONS = [
    "Christian",
    "Jude",
    "Islam",
    "Buddhism",
    "Hinduism",
    "Sikhism",
    "Other"
]

def addReligionsChoices(apps, schema_editor):
  
    for choice in RELIGIONS:
        Religion.objects.get_or_create(name=choice)

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0014_drinkchoice_educationtypes_familyplanchoice_and_more'),  # Include the correct previous migration
    ]

    operations = [
        migrations.RunPython(addReligionsChoices)
    ]