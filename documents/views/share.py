# documents/views/share.py

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from documents.models import Document
from documents.services import share_document, unshare_document, change_document_role
from core.permissions import can_manage_permissions


@csrf_exempt
@require_POST
def share_document_view(request, document_id):
    """
    POST /documents/<id>/share/
    Params: target_username, role
    """
    user = request.user
    doc = get_object_or_404(Document, pk=document_id)

    if not can_manage_permissions(user, doc):
        return JsonResponse({'error': 'Forbidden'}, status=403)

    target_username = request.POST.get("target_username")
    role = request.POST.get("role")

    if not target_username or not role:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    target = get_object_or_404(User, username=target_username)

    try:
        share_document(doc, user, target, role)
        return JsonResponse({'status': 'shared', 'user': target.username, 'role': role})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def unshare_document_view(request, document_id):
    """
    POST /documents/<id>/unshare/
    Params: target_username
    """
    user = request.user
    doc = get_object_or_404(Document, pk=document_id)

    if not can_manage_permissions(user, doc):
        return JsonResponse({'error': 'Forbidden'}, status=403)

    target_username = request.POST.get("target_username")
    if not target_username:
        return JsonResponse({'error': 'Missing target_username'}, status=400)

    target = get_object_or_404(User, username=target_username)

    try:
        unshare_document(doc, user, target)
        return JsonResponse({'status': 'unshared', 'user': target.username})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def change_role_view(request, document_id):
    """
    POST /documents/<id>/change-role/
    Params: target_username, new_role
    """
    user = request.user
    doc = get_object_or_404(Document, pk=document_id)

    if not can_manage_permissions(user, doc):
        return JsonResponse({'error': 'Forbidden'}, status=403)

    target_username = request.POST.get("target_username")
    new_role = request.POST.get("new_role")

    if not target_username or not new_role:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    target = get_object_or_404(User, username=target_username)

    try:
        change_document_role(doc, user, target, new_role)
        return JsonResponse({'status': 'role_changed', 'user': target.username, 'role': new_role})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
