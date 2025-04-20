# documents/views/access.py

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from documents.models import Document
from core.permissions import can_manage_permissions
from core.access import update_access

@require_POST
@login_required
def update_document_access(request, doc_id):
	document = get_object_or_404(Document, id=doc_id, active=True)
	if not can_manage_permissions(request.user, document):
		return JsonResponse({"error": "Forbidden"}, status=403)

	username = request.POST.get("username")
	role = request.POST.get("role")
	remove = request.POST.get("remove") == "1"

	if not username:
		return JsonResponse({"error": "Username required"}, status=400)

	target_user = User.objects.filter(username=username).first()
	if not target_user:
		return JsonResponse({"error": "User not found"}, status=404)

	result = update_access(actor=request.user, target_user=target_user, container=document, role=role, remove=remove)
	if "error" in result:
		return JsonResponse(result, status=400)
	return JsonResponse(result)

