# Generated by Django 4.2.5 on 2023-11-30 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0051_Package_Data_Migrations'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 0), (1, 1), (2, 2)], default=0),
        ),
    ]