# Generated by Django 4.2.5 on 2023-09-28 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_userprofile_cover_photo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coverphoto',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='users/cover_photos/'),
        ),
    ]