# Generated by Django 4.2.5 on 2023-10-17 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0042_alter_userprofile_height'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='address_line1',
            new_name='company',
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='address_line2',
            new_name='job_title',
        ),
    ]
