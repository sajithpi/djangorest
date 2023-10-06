from django.db import migrations
from ..models import DrinkChoice
def addDrinkChoices(apps, schema_editor):
    # DrinkChoice = apps.get('accounts','DrinkChoice')
    DrinkChoice.objects.create(name='Frequently')
    DrinkChoice.objects.create(name='Socially')
    DrinkChoice.objects.create(name='Rarely')
    DrinkChoice.objects.create(name='Never')
    DrinkChoice.objects.create(name='Sober')
    DrinkChoice.objects.create(name='Skip')
    
class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0014_drinkchoice_educationtypes_familyplanchoice_and_more'),  # Include the correct previous migration
    ]

    operations = [
        migrations.RunPython(addDrinkChoices)
    ]