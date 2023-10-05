from django.db import migrations
from ..models import FamilyPlanChoice, Workouts, Religions, RelationShipGoals, SmokeChoices, EducationTypes

def addFamilyPlanChoices(apps, schema_editor):
    # DrinkChoice = apps.get('accounts','DrinkChoice')
    FamilyPlanChoice.objects.create(name='I want children')
    FamilyPlanChoice.objects.create(name="I don't want children")
    FamilyPlanChoice.objects.create(name="I have children and want more")
    FamilyPlanChoice.objects.create(name='I have children and dont want more')
    FamilyPlanChoice.objects.create(name='Not sure yet')
    
class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0014_drinkchoice_educationtypes_familyplanchoice_and_more'),  # Include the correct previous migration
    ]

    operations = [
        migrations.RunPython(addFamilyPlanChoices)
    ]