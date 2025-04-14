# projects/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from projects.models import Project, ProjectMembership
from .forms import ProjectForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from auditlog.models import ShareActionLog

@login_required
def project_list(request):
    projects = Project.objects.filter(active=True).order_by("-created_at")
    roles = {
        m.project_id: m.role
        for m in ProjectMembership.objects.filter(user=request.user)
    }
    return render(request, "projects/project_list.html", {
        "projects": projects,
        "user_roles": roles
    })

@login_required
def project_detail(request, project_id):
	project = get_object_or_404(Project, id=project_id, active=True)

	membership = ProjectMembership.objects.filter(project=project, user=request.user).first()
	user_role = membership.role if membership else None

	members = ProjectMembership.objects.filter(project=project).select_related("user")
	documents = project.documents.all()

	from django.contrib.auth.models import User
	all_users = User.objects.exclude(id=request.user.id).order_by("username")
	
	current_roles = {
		member.user.username: member.role
		for member in members
	}

	return render(request, "projects/project_detail.html", {
		"project": project,
		"user_role": user_role,
		"members": members,
		"documents": documents,
		"all_users": User.objects.exclude(id=request.user.id).order_by("username"),
		"current_roles": current_roles,
	})

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()

            # Create membership assigning creator as owner
            ProjectMembership.objects.create(
                project=project,
                user=request.user,
                role="owner"
            )

            return redirect('projects:detail', project_id=project.pk)
    else:
        form = ProjectForm()

    return render(request, 'projects/project_create.html', {'form': form})

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Optional restriction: only creator can edit
    if project.created_by != request.user:
        return render(request, "403.html", status=403)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects:detail', project_id=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/project_edit.html', {
        'form': form,
        'project': project
    })
	
@login_required
def manage_access(request, project_id):
    # Placeholder view to enable reverse URL resolution
    return render(request, "projects/manage_access.html", {"project_id": project_id})
	
@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, active=True)

    # Restrict to owner via ProjectMembership (not just creator)
    membership = ProjectMembership.objects.filter(project=project, user=request.user).first()
    if not membership or membership.role != "owner":
        return render(request, "403.html", status=403)

    if request.method == "POST":
        project.active = False
        project.save()
        messages.success(request, "Project deleted successfully.")
        return redirect("projects:list")

    return render(request, "projects/confirm_delete.html", {"project": project})
	
@require_POST
@login_required
def update_project_access(request, project_id):
	project = get_object_or_404(Project, id=project_id, active=True)
	membership = ProjectMembership.objects.filter(project=project, user=request.user).first()
	if not membership or membership.role != "owner":
		return JsonResponse({"error": "Only owners can modify access."}, status=403)

	target_username = request.POST.get("username")
	role = request.POST.get("role")
	remove = request.POST.get("remove") == "1"

	if not target_username:
		return JsonResponse({"error": "Username is required."}, status=400)

	target_user = User.objects.filter(username=target_username).first()
	if not target_user:
		return JsonResponse({"error": "User not found."}, status=404)

	entry = ProjectMembership.objects.filter(project=project, user=target_user).first()

	if remove:
		if entry:
			entry.delete()
			
			ShareActionLog.objects.create(
				actor=request.user,
				target_user=target_user,
				project=project,
				action="unshared",
				role=None
			)
			
			return JsonResponse({"success": True, "removed": True, "username": target_user.username})
		else:
			return JsonResponse({"error": "User is not a member."}, status=404)

	if role not in ["owner", "editor", "viewer"]:
		return JsonResponse({"error": "Invalid role."}, status=400)

	entry, created = ProjectMembership.objects.get_or_create(project=project, user=target_user)
	entry.role = role
	entry.save()
	
	action = "shared" if created else "role_changed"
	ShareActionLog.objects.create(
		actor=request.user,
		target_user=target_user,
		project=project,
		role=role,
		action=action
	)

	return JsonResponse({"success": True, "created": created, "role": role, "username": target_user.username})

	