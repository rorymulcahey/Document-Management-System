# auditlog/filters.py

from django.db.models import Q
from auditlog.models import ShareActionLog
from django.contrib.auth.models import User
from typing import Optional
from datetime import datetime


def filter_logs(
    *,
    document_id: Optional[int] = None,
    actor_username: Optional[str] = None,
    target_username: Optional[str] = None,
    action: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> list[ShareActionLog]:
    """
    Filter audit logs using various optional parameters.

    Args:
        document_id: ID of the document whose logs are being queried.
        actor_username: Username of the user who performed the action.
        target_username: Username of the affected user.
        action: Action string ("shared", "unshared", "role_changed").
        since: Only include logs after this datetime.
        until: Only include logs before this datetime.

    Returns:
        List of ShareActionLog entries matching the filter.
    """
    qs = ShareActionLog.objects.all()

    if document_id:
        qs = qs.filter(document_id=document_id)

    if actor_username:
        qs = qs.filter(actor__username=actor_username)

    if target_username:
        qs = qs.filter(target_user__username=target_username)

    if action:
        qs = qs.filter(action=action)

    if since:
        qs = qs.filter(timestamp__gte=since)

    if until:
        qs = qs.filter(timestamp__lte=until)

    return qs.order_by("-timestamp")
