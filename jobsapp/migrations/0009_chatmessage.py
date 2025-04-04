# Generated by Django 3.2.16 on 2025-02-26 09:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_user_options_user_address_user_bio_and_more'),
        ('jobsapp', '0008_applicant_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='accounts.user')),
                ('related_job', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jobsapp.job')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to='accounts.user')),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
    ]
