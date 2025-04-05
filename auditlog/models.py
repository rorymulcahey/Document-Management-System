# auditlog/models.py

from django.db import models
from django.contrib.auth.models import User
from documents.models import Document
from projects.models import Project


class ShareActionLog(models.Model):
    """Logs all permission changes related to document sharing."""

    ACTION_CHOICES = [
        ("shared", "Shared"),
        ("unshared", "Unshared"),
        ("role_changed", "Role Changed"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)

    # Who performed the action
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="audit_actor")

    # Target of the action (user who got access or lost it)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="audit_target")

    # What role was affected
    role = models.CharField(max_length=32)

    # What happened
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)

    # Where it happened
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.timestamp} - {self.actor} {self.action} {self.role} for {self.target_user} on {self.document}"
