# projects/models.py

from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    """
    Represents a logical workspace or team area.
    """
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ProjectMembership(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("editor", "Editor"),
        ("viewer", "Viewer"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ("project", "user")

    def __str__(self):
        return f"{self.user.username} – {self.role} in {self.project.name}"

