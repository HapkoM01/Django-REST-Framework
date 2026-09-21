from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Создаёт группу moderators, если её ещё нет'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='moderators')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "moderators" создана'))
        else:
            self.stdout.write(self.style.WARNING('Группа "moderators" уже существует'))
