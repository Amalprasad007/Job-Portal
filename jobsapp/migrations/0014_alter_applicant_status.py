# Generated by Django 5.1.5 on 2025-02-27 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobsapp', '0013_auto_20250226_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicant',
            name='status',
            field=models.CharField(choices=[('waiting', 'Waiting'), ('shortlisted', 'Shortlisted'), ('rejected', 'Rejected')], default='waiting', max_length=20),
        ),
    ]
