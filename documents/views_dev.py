# documents/views_dev.py

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import redirect
from projects.models import ProjectMembership
from django.conf import settings

# Usage:
# http://localhost:8000/dev/switch-role/1/commenter
# http://localhost:8000/dev/switch-role/1/editor
# http://localhost:8000/dev/switch-role/1/owner


@login_required
def switch_role(request, project_id, role):
	if not settings.DEBUG:
		return HttpResponseForbidden("Only admins can switch roles.")

	membership, _ = ProjectMembership.objects.get_or_create(user=request.user, project_id=project_id)
	membership.role = role
	membership.save()
	messages.success(request, f"Switched role to {role}")
	return redirect("documents:list")
