# Generated by Django 4.2.5 on 2023-10-17 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0043_rename_address_line1_userprofile_company_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='state',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_edited',
            field=models.BooleanField(default=False),
        ),
    ]
