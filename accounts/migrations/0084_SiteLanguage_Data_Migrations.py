from django.db import migrations
from accounts.models import SiteLanguage
def site_languages(apps, schema_editor):

    # Seed initial values
    SiteLanguage.objects.create(language_code='en', site_language='english', language_logo='/site_languages/united-states-of-america.png')
    SiteLanguage.objects.create(language_code='zh', site_language='Mandarin Chinese', language_logo='/site_languages/china.png')
    SiteLanguage.objects.create(language_code='es', site_language='Spanish', language_logo='/site_languages/flag.png')
    SiteLanguage.objects.create(language_code='ru', site_language='Russian', language_logo='/site_languages/russia.png')
class Migration(migrations.Migration):

    dependencies = [
      ('accounts', '0083_sitelanguage_user_site_language'),  # Include the correct previous migration
    ]

    operations = [

        migrations.RunPython(site_languages),  # Add this line to run the Python code
    ]