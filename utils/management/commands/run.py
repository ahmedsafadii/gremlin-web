from django.core.management.base import BaseCommand
from django.core import management


class Command(BaseCommand):
    help = "Fast runserver command with ssl and certificate"

    def handle(self, *args, **options):
        management.call_command("makemigrations")
        management.call_command("migrate")
        management.call_command("runsslserver", certificate="cert.pem", key="key.pem")
