# Generated by Django 4.2.5 on 2023-10-28 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0047_alter_userprofile_about_me'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='about_me',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
