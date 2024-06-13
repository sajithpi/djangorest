from django.db import migrations
from django.conf import settings
from django.core.files import File
from accounts.models import CompanyData
import os

def default_company_logo():
    dummy_logo_path = os.path.join(settings.MEDIA_ROOT, 'company', 'dummy_logo.png')
    return dummy_logo_path  # Return the path to your default image file

def seed_packages(apps, schema_editor):
    CompanyData.objects.create(
        company_logo=get_default_logo_file(),  # Assign the default logo file correctly
        privacy_policy='privacy policy dummy content',
        terms_and_conditions='terms and conditions dummy content',
    )

def get_default_logo_file():
    default_logo_path = default_company_logo()
    if os.path.exists(default_logo_path):
        with open(default_logo_path, 'rb') as f:
            return File(f)
    return None  # Handle case where default logo doesn't exist or couldn't be opened

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0073_companydata_configurations'),  # Include the correct previous migration
    ]

    operations = [
        migrations.RunPython(seed_packages),
    ]