# Generated by Django 4.2.5 on 2023-11-02 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0006_travelrequests'),
    ]

    operations = [
        migrations.AddField(
            model_name='travelrequests',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='travelrequests',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
