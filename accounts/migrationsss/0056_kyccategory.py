# Generated by Django 4.2.5 on 2023-12-04 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0055_alter_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='KycCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
            ],
        ),
    ]
