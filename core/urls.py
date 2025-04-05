# core/urls.py

from django.urls import include, path

urlpatterns = [
    path("documents/", include("documents.urls", namespace="documents")),
    path("projects/", include("projects.urls", namespace="projects")),
    path("users/", include("users.urls", namespace="users")),
    path("audit/", include("auditlog.urls", namespace="auditlog")),
]
