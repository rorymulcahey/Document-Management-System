# auditlog/management/commands/seed_audit_logs.py

import csv
from django.core.management.base import BaseCommand
from auditlog.models import ShareActionLog
from documents.models import Document
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime

class Command(BaseCommand):
    help = "Seed the audit log table from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **kwargs):
        path = kwargs["csv_path"]
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                try:
                    document = Document.objects.get(pk=row["document_id"])
                    actor = User.objects.get(pk=row["actor_id"])
                    target = User.objects.get(pk=row["target_id"])
                    ShareActionLog.objects.create(
                        timestamp=parse_datetime(row["timestamp"]),
                        role=row["role"],
                        action=row["action"],
                        document=document,
                        project=document.project,
                        actor=actor,
                        target_user=target,
                    )
                    count += 1
                except Exception as e:
                    self.stderr.write(f"Error on row {row['id']}: {e}")
            self.stdout.write(self.style.SUCCESS(f"Seeded {count} audit log entries"))
