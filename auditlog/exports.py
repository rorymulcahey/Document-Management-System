# auditlog/exports.py

import csv
from io import StringIO
from typing import Iterable
from auditlog.models import ShareActionLog


def export_logs_to_csv(logs: Iterable[ShareActionLog]) -> str:
    """
    Convert audit logs to a CSV string for export.

    Args:
        logs: QuerySet or iterable of ShareActionLog objects

    Returns:
        CSV-formatted string
    """
    buffer = StringIO()
    writer = csv.writer(buffer)

    # Header row
    writer.writerow([
        "Timestamp",
        "Actor",
        "Target User",
        "Role",
        "Action",
        "Document",
        "Project"
    ])

    for log in logs:
        writer.writerow([
            log.timestamp.isoformat(),
            log.actor.username if log.actor else "",
            log.target_user.username if log.target_user else "",
            log.role,
            log.action,
            log.document.title if log.document else "",
            log.project.name if log.project else "",
        ])

    return buffer.getvalue()
