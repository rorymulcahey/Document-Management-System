# auditlog/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse
from documents.models import Document
from auditlog.filters import filter_logs
from core.permissions import can_manage_permissions
from auditlog.models import ShareActionLog
from auditlog.exports import export_logs_to_csv

@login_required
def audit_log_filtered_view(request, document_id):
    document = get_object_or_404(Document, id=document_id, active=True)

    # Base queryset
    logs = ShareActionLog.objects.filter(document=document).select_related("actor", "target_user")

    # GET filters
    actor = request.GET.get("actor", "").strip()
    target = request.GET.get("target", "").strip()
    action = request.GET.get("action", "").strip()
    role = request.GET.get("role", "").strip()

    if actor:
        logs = logs.filter(actor__username__icontains=actor)
    if target:
        logs = logs.filter(target_user__username__icontains=target)
    if action:
        logs = logs.filter(action=action)
    if role:
        logs = logs.filter(role=role)

    return render(request, "auditlog/log_list.html", {
        "document": document,
        "logs": logs,
        "filters": {
            "actor": actor,
            "target": target,
            "action": action,
            "role": role,
        },
    })

@login_required
def audit_log_export_csv(request, document_id):
	document = get_object_or_404(Document, id=document_id, active=True)

	if not can_manage_permissions(request.user, document):
		return HttpResponse(status=403, content="Permission denied.")

	logs = ShareActionLog.objects.filter(document=document).select_related("actor", "target_user", "project")
	csv_content = export_logs_to_csv(logs)

	response = HttpResponse(csv_content, content_type="text/csv")
	response["Content-Disposition"] = f'attachment; filename="audit_log_{document_id}.csv"'
	return response

@login_required
def project_audit_log_view(request, project_id):
	from projects.models import Project, ProjectMembership

	project = get_object_or_404(Project, id=project_id, active=True)
	membership = ProjectMembership.objects.filter(project=project, user=request.user).first()
	if not request.user.is_superuser and (not membership or membership.role != "owner"):
		return render(request, "403.html", status=403)

	logs = ShareActionLog.objects.filter(project=project).select_related("actor", "target_user")

	# Filters
	actor = request.GET.get("actor", "").strip()
	target = request.GET.get("target", "").strip()
	action = request.GET.get("action", "").strip()
	role = request.GET.get("role", "").strip()

	if actor:
		logs = logs.filter(actor__username__icontains=actor)
	if target:
		logs = logs.filter(target_user__username__icontains=target)
	if action:
		logs = logs.filter(action=action)
	if role:
		logs = logs.filter(role=role)

	return render(request, "auditlog/log_list.html", {
		"project": project,
		"logs": logs,
		"document": None,
		"filters": {
			"actor": actor,
			"target": target,
			"action": action,
			"role": role,
		},
	})
