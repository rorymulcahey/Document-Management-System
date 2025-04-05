# documents/importers/models.py

from django.db import models
from projects.models import Project
from django.contrib.auth.models import User


class SharePointImportLog(models.Model):
    """Captures per-row import metadata from SharePoint."""
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    success = models.BooleanField(default=True)
    error_detail = models.TextField(blank=True)
    detected_powerbi = models.BooleanField(default=False)
    source_site = models.CharField(max_length=255, blank=True)
    source_list = models.CharField(max_length=255, blank=True)
    raw_row = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.title} (Success={self.success})"
