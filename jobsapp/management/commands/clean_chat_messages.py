from django.core.management.base import BaseCommand
from jobsapp.models import ChatMessage

class Command(BaseCommand):
    help = 'Clean up chat messages'

    def handle(self, *args, **options):
        # Delete all existing messages
        ChatMessage.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully cleaned up chat messages'))
