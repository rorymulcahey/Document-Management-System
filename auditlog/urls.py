# auditlog/urls.py

from django.urls import path
from auditlog import views

app_name = "auditlog"

urlpatterns = [
    # View audit logs for a specific document (filtered)
    path(
        "documents/<int:document_id>/logs/",
        views.audit_log_filtered_view,
        name="filtered_logs",
    ),
    path("documents/<int:document_id>/logs/export/", views.audit_log_export_csv, name="export_csv"),
]
