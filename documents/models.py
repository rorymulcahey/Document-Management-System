# documents/models.py

from django.db import models
from django.contrib.auth.models import User
from projects.models import Project


class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='created_documents')
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
	
    class Meta:
        permissions = [
            ("owner_document", "Can own document"),
            ("editor_document", "Can edit document"),
            ("commenter_document", "Can comment on document"),
        ]

    def latest_version(self):
        return self.versions.order_by('-version_number').first()

    def __str__(self):
        return f"{self.title} (Project: {self.project})"


class DocumentVersion(models.Model):
    """
    Represents a specific version of a document.
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    file = models.FileField(upload_to='documents/%Y/%m/')
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('document', 'version_number')
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.document.title} v{self.version_number}"


class Comment(models.Model):
    """
    Comments tied to a specific document version.
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comments')
    version = models.ForeignKey(DocumentVersion, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.document} v{self.version.version_number if self.version else 'latest'}"
