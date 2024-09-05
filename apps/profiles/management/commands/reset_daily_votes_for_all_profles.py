from django.core.management.base import BaseCommand

from apps.profiles.tasks import reset_daily_votes_for_all_profles


class Command(BaseCommand):
    help = "Run the celery reset user daily votes task as a management command"

    def handle(self, *args, **options):
        reset_daily_votes_for_all_profles()
