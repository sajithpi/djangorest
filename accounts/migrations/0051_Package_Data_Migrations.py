from django.db import migrations
from accounts.models import Package
def seed_packages(apps, schema_editor):

    # Seed initial values
    Package.objects.create(name='Free Package', price=0, type='Free',  package_img = '', validity=0)
    Package.objects.create(name='Paid Package', price=10, type='Paid', package_img = '', validity=6)
    Package.objects.create(name='Paid Package', price=10, type='Paid', package_img = '', validity=1)

class Migration(migrations.Migration):

    dependencies = [
      ('accounts', '0050_package_user_package_validity_order_user_package'),  # Include the correct previous migration
    ]

    operations = [

        migrations.RunPython(seed_packages),  # Add this line to run the Python code
    ]