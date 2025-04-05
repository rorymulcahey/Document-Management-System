# core/admin.py

from django.contrib import admin
from documents.models import Document, DocumentVersion, Comment

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "created_by", "created_at")
    search_fields = ("title", "description")
    list_filter = ("project", "created_by")
    ordering = ("-created_at",)


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ("document", "version_number", "uploaded_by", "uploaded_at")
    search_fields = ("document__title", "notes")
    ordering = ("-uploaded_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("document", "user", "created_at")
    search_fields = ("document__title", "user__username", "body")
    ordering = ("-created_at",)
