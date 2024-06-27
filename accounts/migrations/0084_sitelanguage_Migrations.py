from django.db import migrations
from ..models import SiteLanguage

SITE_LANGUAGES = [
    "en",
    "zh",
    "es",
    "ru"
]

def addSiteLanguages(apps, schema_editor):
  
    for choice in SITE_LANGUAGES:
        SiteLanguage.objects.get_or_create(site_language=choice)

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0083_sitelanguage'),  # Include the correct previous migration
    ]

    operations = [
        migrations.RunPython(addSiteLanguages)
    ]