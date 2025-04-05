# core/permissions.py

from guardian.shortcuts import get_perms
from documents.models import Document
from django.contrib.auth.models import User

"""
Permission Utilities
--------------------
Centralized logic for role-based access checks.
Used across views, services, forms, and templates.
"""

ROLE_PERM_MAP = {
    "owner": "owner_document",
    "editor": "editor_document",
    "commenter": "commenter_document"
}

def has_document_role(user: User, document: Document, role: str) -> bool:
    """
    Returns True if the user has the given role for the document.
    """
    if not user or not document or role not in ROLE_PERM_MAP:
        return False

    return ROLE_PERM_MAP[role] in get_perms(user, document)


def get_user_document_role(user: User, document: Document) -> str | None:
    """
    Returns the highest role a user has for a given document, or None.
    Role hierarchy: owner > editor > commenter
    """
    if not user or not document:
        return None

    perms = set(get_perms(user, document))

    if ROLE_PERM_MAP["owner"] in perms:
        return "owner"
    if ROLE_PERM_MAP["editor"] in perms:
        return "editor"
    if ROLE_PERM_MAP["commenter"] in perms:
        return "commenter"
    return None


def can_edit_document(user: User, document: Document) -> bool:
    return has_document_role(user, document, "editor") or has_document_role(user, document, "owner")


def can_comment_on_document(user: User, document: Document) -> bool:
    return has_document_role(user, document, "commenter") or can_edit_document(user, document)


def can_manage_permissions(user: User, document: Document) -> bool:
    """
    Returns True if the user is the owner of the document and can share/unshare.
    """
    return has_document_role(user, document, "owner")
