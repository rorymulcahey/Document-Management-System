# auditlog/admin.py

from django.contrib import admin
from auditlog.models import ShareActionLog


@admin.register(ShareActionLog)
class ShareActionLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "actor",
        "target_user",
        "role",
        "action",
        "document",
        "project",
    )
    list_filter = (
        "action",
        "role",
        "timestamp",
        "project",
    )
    search_fields = (
        "actor__username",
        "target_user__username",
        "document__title",
        "project__name",
    )
    ordering = ("-timestamp",)
