# projects/admin.py

from django.contrib import admin
from projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at")
    search_fields = ("name", "description", "created_by__username")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)

