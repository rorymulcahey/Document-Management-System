# core/signals.py

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.auth.models import AnonymousUser
from documents.models import Document, DocumentVersion, Comment
from projects.models import Project


def get_request_user(instance):
    """
    Optional hook: Try to retrieve request user if available.
    Expects `instance._request_user` to be set externally in views/forms.
    """
    return getattr(instance, "_request_user", None)


@receiver(pre_save, sender=Document)
@receiver(pre_save, sender=DocumentVersion)
@receiver(pre_save, sender=Comment)
@receiver(pre_save, sender=Project)
def track_user_modification(sender, instance, **kwargs):
    """
    Auto-fill created_by and modified_by fields on tracked models.
    Assumes views/forms set instance._request_user prior to save.
    """
    user = get_request_user(instance)
    if not user or isinstance(user, AnonymousUser):
        return

    # If the model has a created_by and it's not yet set
    if hasattr(instance, "created_by") and not instance.created_by:
        instance.created_by = user

    if hasattr(instance, "modified_by"):
        instance.modified_by = user
