# Generated by Django 4.2.5 on 2023-11-29 08:33

import chat.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_rename_receiver_profile_roomchat_receiverprofile_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sticker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, null=True, upload_to=chat.models.stickers_upload_path)),
            ],
        ),
    ]
