from django.db import migrations
from accounts.models import Configurations
def seed_packages(apps, schema_editor):

   
    
    Configurations.objects.create(company_name='datingApp', 
                                  company_mail='tl_python1@teamioss.com',
                                  email_host='smtp.gmail.com',
                                  email_port = 587,
                                  email_host_user = 'tl_python1@teamioss.com',
                                  email_host_password = 'nkioragcmtwubkml',
                                  email_tls = True,
                                  paypal_client_id = "AUOCdFYdYDW6GF5vAYNeNE5-zV0jrQen_GtID1Cvs9I0UmODkjW4Iosbesmfc2pN0maIaJTYnJKeZFH8",
                                  paypal_client_secret = "EPoUKJRlakbNRVhXm_rov7qG7oHThRhXuevafcVoYA839YaLxklkWqYYS8C6zkkws4sT4AS4OOhzB1nv",
                                  paypal_base_url = "api.sandbox.paypal.com",
                                  welcome_mail = True,
                                  company_address = "dating App, cyber park"
                                  )
    
class Migration(migrations.Migration):

    dependencies = [
      ('accounts', '0074_CompanyData_Migrations'),  # Include the correct previous migration
    ]

    operations = [

        migrations.RunPython(seed_packages),  # Add this line to run the Python code
    ]