# Generated by Django 4.2.5 on 2023-10-16 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0040_rename_feet_userprofile_height_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='height',
            field=models.FloatField(blank=True, null=True),
        ),
    ]