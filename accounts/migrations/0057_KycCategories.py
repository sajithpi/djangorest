from django.db import migrations
from ..models import KycCategory

CATEGORIES = [
    "ID Card & Proof of Adress",
    "Driver Licence & Proof of Address",
    "Passport &  Proof of Address",
]

def addKycChoices(apps, schema_editor):
  
    for choice in CATEGORIES:
        KycCategory.objects.get_or_create(name=choice)

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0056_kyccategory'),  # Include the correct previous migration
    ]

    operations = [
        migrations.RunPython(addKycChoices)
    ]