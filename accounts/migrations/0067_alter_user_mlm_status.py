# Generated by Django 4.2.5 on 2023-12-06 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0066_rename_mlm_choice_user_mlm_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='mlm_status',
            field=models.CharField(blank=True, choices=[('inactive', 'inactive'), ('active', 'active')], default='inactive', max_length=8, null=True),
        ),
    ]