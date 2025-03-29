from django.db import migrations

def update_status(apps, schema_editor):
    Applicant = apps.get_model('jobsapp', 'Applicant')
    Applicant.objects.filter(status='shortlisted').update(status='accepted')

class Migration(migrations.Migration):
    dependencies = [
        ('jobsapp', '0010_alter_applicant_status'),
    ]

    operations = [
        migrations.RunPython(update_status),
    ]
