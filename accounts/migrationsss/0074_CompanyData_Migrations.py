from django.db import migrations
from accounts.models import CompanyData
def seed_packages(apps, schema_editor):

   
    
    CompanyData.objects.create(privacy_policy='privacy policy dummy content', terms_and_conditions='terms and conditions dummy content',)
    
class Migration(migrations.Migration):

    dependencies = [
      ('accounts', '0073_companydata_configurations'),  # Include the correct previous migration
    ]

    operations = [

        migrations.RunPython(seed_packages),  # Add this line to run the Python code
    ]