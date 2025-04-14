# auditlog/urls.py

from django.urls import path
from auditlog import views

app_name = "auditlog"

urlpatterns = [

    path("documents/<int:document_id>/logs/", views.audit_log_filtered_view, name="filtered_logs",),
    path("documents/<int:document_id>/logs/export/", views.audit_log_export_csv, name="export_csv"),
	path("documents/<int:document_id>/audit/", views.audit_log_filtered_view, name="doc_logs"),

	path("projects/<int:project_id>/logs/", views.project_audit_log_view, name="project_logs"),
	path("projects/<int:project_id>/logs/export/", views.project_log_export_csv, name="project_logs_export"),
]
