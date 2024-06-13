from django.db import migrations
from django.conf import settings
from django.core.files import File
from accounts.models import CompanyData
import os

def seed_packages(apps, schema_editor):

   
    
    CompanyData.objects.create(company_logo=get_dummy_logo(), 
                            privacy_policy='privacy policy dummy content',
                            terms_and_conditions='terms and conditions dummy content',)
    
def get_dummy_logo():
    # Example function to provide a dummy image file if company_logo is null
    dummy_logo_path = os.path.join(settings.MEDIA_ROOT, 'company', 'dating-app.jpg')
    if os.path.exists(dummy_logo_path):
        with open(dummy_logo_path, 'rb') as f:
            return File(f)
    return None  # Handle case where dummy logo doesn't exist
    
class Migration(migrations.Migration):

    dependencies = [
      ('accounts', '0073_companydata_configurations'),  # Include the correct previous migration
    ]

    operations = [

        migrations.RunPython(seed_packages),  # Add this line to run the Python code
    ]