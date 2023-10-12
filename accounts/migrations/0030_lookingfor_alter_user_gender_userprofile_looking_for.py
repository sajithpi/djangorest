# Generated by Django 4.2.5 on 2023-10-12 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0029_profilepreference'),
    ]

    operations = [
        migrations.CreateModel(
            name='LookingFor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('TM', 'Transman'), ('TW', 'Transwomen')], max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='looking_for',
            field=models.ManyToManyField(blank=True, null=True, related_name='users', to='accounts.lookingfor'),
        ),
    ]
