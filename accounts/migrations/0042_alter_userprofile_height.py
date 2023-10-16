# Generated by Django 4.2.5 on 2023-10-16 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0041_alter_userprofile_height'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='height',
            field=models.FloatField(blank=True, null=True, verbose_name='Height in cm'),
        ),
    ]
