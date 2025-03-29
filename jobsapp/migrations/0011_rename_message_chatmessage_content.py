from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('jobsapp', '0010_alter_applicant_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatmessage',
            old_name='message',
            new_name='content',
        ),
        migrations.RenameField(
            model_name='chatmessage',
            old_name='timestamp',
            new_name='created_at',
        ),
    ]
