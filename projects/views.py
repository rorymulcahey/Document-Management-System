# projects/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from projects.models import Project, ProjectMembership
from .forms import ProjectForm
from django.contrib import messages

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

    # Get role from membership table
    membership = ProjectMembership.objects.filter(project=project, user=request.user).first()
    user_role = membership.role if membership else None

    members = ProjectMembership.objects.filter(project=project).select_related("user")
    documents = project.documents.all()  # using related_name='documents'

    return render(request, "projects/project_detail.html", {
        "project": project,
        "user_role": user_role,
        "members": members,
        "documents": documents
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
	