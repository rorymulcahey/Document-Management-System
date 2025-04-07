# documents/views/document.py

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from documents.models import Document
from documents.forms import DocumentUploadForm, DocumentForm
from core.permissions import (can_edit_document, has_document_role, get_user_document_role,can_comment_on_document, can_manage_permissions)
from projects.models import ProjectMembership
from core.permissions import get_user_document_role, can_edit_document, can_comment_on_document
from django.contrib import messages
from django.contrib.auth.models import User
from projects.models import Project

@login_required
def document_list(request):
	user = request.user

	# Base queryset with access restriction
	queryset = Document.objects.filter(active=True, project__memberships__user=user).distinct()

	# === Filtering logic ===
	title_query = request.GET.get("title", "").strip()
	project_id = request.GET.get("project")
	uploaded_by_id = request.GET.get("uploaded_by")

	if title_query:
		queryset = queryset.filter(title__icontains=title_query)
	if project_id:
		queryset = queryset.filter(project_id=project_id)
	if uploaded_by_id:
		queryset = queryset.filter(created_by_id=uploaded_by_id)

	# Preload all user memberships
	memberships = ProjectMembership.objects.filter(user=request.user).select_related("project")
	membership_map = {m.project_id: m.role for m in memberships}

	# Role per document based on project
	user_roles = {doc.id: membership_map.get(doc.project_id, "member") for doc in queryset}

	# Permission flags (for template use)
	can_edit = {doc.id: can_edit_document(request.user, doc) for doc in queryset}
	can_comment = {doc.id: can_comment_on_document(request.user, doc) for doc in queryset}

	# For dropdowns
	accessible_projects = Project.objects.filter(id__in=queryset.values("project_id"))
	uploading_users = User.objects.filter(id__in=queryset.values("created_by_id"))
	
	return render(request, "documents/document_list.html", {
		"documents": queryset.select_related("project", "created_by"),
		"user_roles": user_roles,
		"can_edit": can_edit,
		"can_comment": can_comment,
		"projects": accessible_projects,
		"users": uploading_users,
		"title_query": title_query,
		"project_id": project_id,
		"uploaded_by_id": uploaded_by_id,
	})


@login_required
def document_detail(request, doc_id):
	document = get_object_or_404(Document, id=doc_id, active=True)

	versions = document.versions.all()
	comments = document.comments.select_related("user", "version")
	user_role = get_user_document_role(request.user, document)
	can_edit = can_edit_document(request.user, document)
	can_comment = can_comment_on_document(request.user, document)
	can_manage = can_manage_permissions(request.user, document)

	return render(request, "documents/document_detail.html", {
		"document": document,
		"versions": versions,
		"comments": comments,
		"user_role": user_role,
		"can_edit": can_edit,
		"can_comment": can_comment,
		"can_manage": can_manage,
    })


@login_required
def upload_version(request, doc_id):
    """
    Upload a new version of an existing document.
    """
    document = get_object_or_404(Document, id=doc_id)

    if not can_edit_document(request.user, document):
        return HttpResponseForbidden("You do not have permission to upload to this document.")

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES, user=request.user, document=document)
        if form.is_valid():
            form.save()
            return redirect("documents:detail", doc_id=document.id)
    else:
        form = DocumentUploadForm(user=request.user, document=document)

    return render(request, "documents/upload_version.html", {
        "form": form,
        "document": document,
    })

@login_required
def document_create(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.created_by = request.user
            doc.save()
            return redirect("documents:detail", doc_id=doc.id)
    else:
        form = DocumentForm()
    return render(request, "documents/document_form.html", {
    "form": form,
    "editing": False,
	})


@login_required
def document_edit(request, doc_id):
    document = get_object_or_404(Document, pk=doc_id)

    if not can_edit_document(request.user, document):
        return redirect("documents:detail", doc_id=doc_id)

    if request.method == "POST":
        form = DocumentForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            return redirect("documents:detail", doc_id=doc_id)
    else:
        form = DocumentForm(instance=document)

    return render(request, "documents/document_form.html", {
        "form": form,
        "document": document,
        "editing": True,
    })

@login_required
def delete_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id, active=True)

    # Only owner of the parent project can delete
    membership = ProjectMembership.objects.filter(project=document.project, user=request.user).first()
    if not membership or membership.role != "owner":
        return HttpResponseForbidden("You do not have permission to delete this document.")

    if request.method == "POST":
        document.active = False
        document.save()
        messages.success(request, "Document deleted successfully.")
        return redirect("documents:list")

    return render(request, "documents/confirm_delete.html", {"document": document})


