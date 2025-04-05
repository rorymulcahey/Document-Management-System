# documents/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta

from documents.models import Document, Comment
from core.permissions import get_user_document_role


@shared_task
def send_document_comment_notification(document_id, comment_id):
    """
    Notify the document owner about a new comment.
    """
    try:
        doc = Document.objects.get(id=document_id)
        comment = Comment.objects.get(id=comment_id)
        owner = doc.created_by

        if not owner or not owner.email:
            return  # No email to send to

        send_mail(
            subject=f"New comment on: {doc.title}",
            message=f"{comment.user.username} commented:\n\n{comment.body}",
            from_email="noreply@example.com",
            recipient_list=[owner.email],
        )
    except Exception as e:
        print(f"[tasks.send_document_comment_notification] Failed: {e}")


@shared_task
def send_periodic_document_reminders():
    """
    Periodic reminder for document owners to review updates, versions, etc.
    This is a placeholder and should be scheduled with Celery beat.
    """
    cutoff = now() - timedelta(days=7)
    docs = Document.objects.filter(created_at__lt=cutoff)

    for doc in docs:
        owner = doc.created_by
        if not owner or not owner.email:
            continue

        latest = doc.latest_version()
        version_info = f"Latest version: v{latest.version_number}" if latest else "No versions uploaded."

        send_mail(
            subject=f"Reminder: Review document '{doc.title}'",
            message=f"This is a reminder to review your document: {doc.title}.\n\n{version_info}",
            from_email="noreply@example.com",
            recipient_list=[owner.email],
        )
