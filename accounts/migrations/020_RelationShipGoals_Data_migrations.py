from django.db import migrations
from ..models import RelationShipGoals

RELATIONSHIP_GOALS = [
    "Find True Love",
    "Make New Friends",
    "Explore New Experiences",
    "Build a Family",
    "Emotional Support",
    "Casual Fun",
    "Travel Partner",
    "Improve Social Skills",
    "Discover Common Interests",
    "Learn About Different",
]

def addRelationShipGoals(apps, schema_editor):
  
    for choice in RELATIONSHIP_GOALS:
        RelationShipGoals.objects.get_or_create(name=choice)

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0014_drinkchoice_educationtypes_familyplanchoice_and_more'),  # Include the correct previous migration
    ]

    operations = [
        migrations.RunPython(RelationShipGoals)
    ]