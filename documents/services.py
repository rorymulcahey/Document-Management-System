# documents/services.py

from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm, remove_perm
from documents.models import Document
from auditlog.models import ShareActionLog
from core.permissions import ROLE_PERM_MAP, can_manage_permissions


def share_document(document: Document, actor: User, target: User, role: str) -> None:
    """
    Assigns a role to a target user for a given document.
    Logs the action.
    """
    if not can_manage_permissions(actor, document):
        raise PermissionError("User lacks permission to share this document.")

    perm = f"documents.{ROLE_PERM_MAP.get(role)}"
    if not perm:
        raise ValueError(f"Invalid role: {role}")

    assign_perm(perm, target, document)

    ShareActionLog.objects.create(
        actor=actor,
        target_user=target,
        role=role,
        action="shared",
        document=document,
        project=document.project
    )


def unshare_document(document: Document, actor: User, target: User) -> None:
    """
    Removes all roles for a user on a document.
    Logs the action.
    """
    if not can_manage_permissions(actor, document):
        raise PermissionError("User lacks permission to unshare this document.")

    # Remove all role-specific perms
    for role, perm_name in ROLE_PERM_MAP.items():
        remove_perm(f"documents.{perm_name}", target, document)

    ShareActionLog.objects.create(
        actor=actor,
        target_user=target,
        role="all",
        action="unshared",
        document=document,
        project=document.project
    )


def change_document_role(document: Document, actor: User, target: User, new_role: str) -> None:
    """
    Changes a user's role by removing old and assigning new.
    Logs the role change.
    """
    if not can_manage_permissions(actor, document):
        raise PermissionError("User lacks permission to change roles.")

    # Remove all first
    for role, perm_name in ROLE_PERM_MAP.items():
        remove_perm(f"documents.{perm_name}", target, document)

    assign_perm(f"documents.{ROLE_PERM_MAP[new_role]}", target, document)

    ShareActionLog.objects.create(
        actor=actor,
        target_user=target,
        role=new_role,
        action="role_changed",
        document=document,
        project=document.project
    )


def assign_document_permissions():
    '''Central logic for assigning viewer/editor roles.'''

def notify_owner_on_comment():
    '''Send email notification to document owner.'''