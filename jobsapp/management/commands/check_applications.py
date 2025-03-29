from django.core.management.base import BaseCommand
from jobsapp.models import Applicant

class Command(BaseCommand):
    help = 'Check applications in the database'

    def handle(self, *args, **options):
        applications = Applicant.objects.all()
        self.stdout.write(f"Total applications: {applications.count()}")
        
        for app in applications:
            self.stdout.write(f"""
Application ID: {app.id}
Job: {app.job.title}
User: {app.user.email}
Status: {app.status}
Created: {app.created_at}
-------------------
""")
