# Generated by Django 4.2.5 on 2023-12-07 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0070_alter_contactus_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactus',
            name='message',
            field=models.CharField(max_length=250),
        ),
    ]
