# Generated by Django 4.2.5 on 2023-11-03 05:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0048_alter_userprofile_about_me'),
        ('travel', '0008_rename_travelrequests_travelrequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyTrip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('location', models.CharField(blank=True, max_length=50, null=True)),
                ('travel_date', models.DateTimeField(blank=True, null=True)),
                ('days', models.PositiveIntegerField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=2500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(blank=True, choices=[('INITIATED', 'INITIATED'), ('COMPLETED', 'COMPLETED'), ('CANCELED', 'CANCELED'), ('PENDING', 'PENDING')], default='INITIATED', max_length=11, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.userprofile')),
            ],
        ),
        migrations.AlterField(
            model_name='travelrequest',
            name='trip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel.mytrip'),
        ),
        migrations.DeleteModel(
            name='TravelPlan',
        ),
    ]
