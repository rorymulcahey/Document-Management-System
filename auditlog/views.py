# auditlog/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from documents.models import Document
from auditlog.filters import filter_logs
from core.permissions import can_manage_permissions
from auditlog.models import ShareActionLog

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
