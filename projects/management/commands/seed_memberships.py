# projects/management/commands/seed_memberships.py

from django.core.management.base import BaseCommand
from projects.models import Project, ProjectMembership
from django.contrib.auth.models import User
import random

class Command(BaseCommand):
    help = "Seed random ProjectMemberships"

    def handle(self, *args, **kwargs):
        roles = ["owner", "editor", "viewer"]
        users = list(User.objects.all())
        count = 0

        for project in Project.objects.all():
            assigned = random.sample(users, k=min(5, len(users)))
            for i, user in enumerate(assigned):
                role = "owner" if i == 0 else random.choice(roles[1:])
                ProjectMembership.objects.get_or_create(project=project, user=user, defaults={"role": role})
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {count} project memberships."))
