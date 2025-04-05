# documents/management/commands/populate_dummy_data.py

import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from projects.models import Project
from documents.models import Document, DocumentVersion, Comment
from auditlog.models import ShareActionLog
from guardian.shortcuts import assign_perm
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = "Populate the database with dummy data for testing."

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating dummy data...")
        self.create_users()
        self.create_projects()
        self.create_documents()
        self.create_comments()
        self.create_audit_logs()
        self.stdout.write(self.style.SUCCESS("Dummy data successfully created."))

    def create_users(self, count=5):
        for _ in range(count):
            User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password="testpass123"
            )

    def create_projects(self, count=5):
        users = list(User.objects.all())
        for _ in range(count):
            Project.objects.create(
                name=fake.unique.company(),
                description=fake.text(),
                created_by=random.choice(users)
            )

    def create_documents(self, count=10):
        projects = list(Project.objects.all())
        users = list(User.objects.all())
        for _ in range(count):
            doc = Document.objects.create(
                project=random.choice(projects),
                title=fake.sentence(nb_words=4),
                description=fake.text(),
                created_by=random.choice(users)
            )
            version_count = random.randint(1, 3)
            for v_num in range(1, version_count + 1):
                DocumentVersion.objects.create(
                    document=doc,
                    version_number=v_num,
                    file=f"documents/dummy_v{v_num}.pdf",
                    notes=fake.sentence(),
                    uploaded_by=random.choice(users)
                )
            assign_perm("documents.owner_document", doc.created_by, doc)

    def create_comments(self, count=30):
        documents = list(Document.objects.all())
        users = list(User.objects.all())
        for _ in range(count):
            Comment.objects.create(
                document=random.choice(documents),
                user=random.choice(users),
                body=fake.text()
            )

    def create_audit_logs(self, count=15):
        documents = list(Document.objects.all())
        users = list(User.objects.all())
        actions = ["shared", "unshared", "role_changed"]
        roles = ["owner", "editor", "commenter"]

        for _ in range(count):
            ShareActionLog.objects.create(
                actor=random.choice(users),
                target_user=random.choice(users),
                role=random.choice(roles),
                action=random.choice(actions),
                document=random.choice(documents),
                project=random.choice(documents).project
            )
