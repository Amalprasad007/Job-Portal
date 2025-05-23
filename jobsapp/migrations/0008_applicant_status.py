# Generated by Django 3.2.16 on 2025-02-26 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobsapp', '0007_alter_applicant_id_alter_job_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicant',
            name='status',
            field=models.CharField(choices=[('waiting', 'Waiting'), ('shortlisted', 'Shortlisted'), ('rejected', 'Rejected')], default='waiting', max_length=20),
        ),
    ]
