# users/views.py

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from documents.models import Document, Comment
from projects.models import Project


@login_required
def user_list(request):
    """
    Display all registered users.
    Useful for admin or team views.
    """
    users = User.objects.all().order_by("username")
    return render(request, "users/user_list.html", {"users": users})


@login_required
def user_profile(request, username):
    """
    Public-facing profile for a given user.
    Includes their created projects and documents.
    """
    user_obj = get_object_or_404(User, username=username)

    created_projects = Project.objects.filter(created_by=user_obj)
    created_documents = Document.objects.filter(created_by=user_obj)
    comments = Comment.objects.filter(user=user_obj)

    return render(request, "users/user_profile.html", {
        "profile_user": user_obj,
        "created_projects": created_projects,
        "created_documents": created_documents,
        "comments": comments,
    })
