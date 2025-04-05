# documents/views/audit.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from auditlog.models import ShareActionLog
from documents.models import Document
from core.permissions import can_manage_permissions


@login_required
def audit_log_view(request, document_id):
    """
    View audit log entries for a specific document.
    Restricted to users who can manage document permissions.
    """
    document = get_object_or_404(Document, id=document_id)

    if not can_manage_permissions(request.user, document):
        return render(request, "403.html", status=403)

    logs = ShareActionLog.objects.filter(document=document).order_by("-timestamp")

    return render(request, "documents/audit_log.html", {
        "document": document,
        "logs": logs,
    })
