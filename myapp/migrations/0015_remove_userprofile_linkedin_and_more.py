# Generated by Django 5.2 on 2025-05-04 10:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0014_organizationprofile_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='linkedin',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='portfolio_website',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='resume',
        ),
    ]
