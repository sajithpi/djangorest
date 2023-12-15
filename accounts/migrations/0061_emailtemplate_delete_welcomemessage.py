# Generated by Django 4.2.5 on 2023-12-05 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0060_welcomemessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('type', models.CharField(blank=True, choices=[('register', 'register'), ('otp', 'otp'),('register', 'register')], max_length=10, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='WelcomeMessage',
        ),
    ]
