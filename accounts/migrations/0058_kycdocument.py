# Generated by Django 4.2.5 on 2023-12-04 08:36

import accounts.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0057_KycCategories'),
    ]

    operations = [
        migrations.CreateModel(
            name='KycDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ImageField(blank=True, null=True, upload_to=accounts.models.kyc_upload_path)),
                ('status', models.SmallIntegerField(choices=[(0, 'Pending'), (1, 'Approved'), (2, 'Rejected')], default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kyc_category', to='accounts.kyccategory')),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kyc_documents', to='accounts.userprofile')),
            ],
        ),
    ]