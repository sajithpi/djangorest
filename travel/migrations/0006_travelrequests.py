# Generated by Django 4.2.5 on 2023-11-02 11:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0048_alter_userprofile_about_me'),
        ('travel', '0005_remove_travelplan_intrested_users'),
    ]

    operations = [
        migrations.CreateModel(
            name='TravelRequests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('status', models.CharField(choices=[(0, 'PENDING'), (1, 'ACCEPTED'), (2, 'REJECTED')], default=0, max_length=1)),
                ('requested_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.userprofile')),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel.travelplan')),
            ],
        ),
    ]