# core/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from documents.models import Document
from core.permissions import has_document_role, get_user_document_role
from django.shortcuts import render
from projects.models import Project

@login_required
def dashboard(request):
    recent_docs = Document.objects.filter(active=True).order_by('-created_at')[:5]
    recent_projects = Project.objects.filter(active=True).order_by('-created_at')[:5]

    return render(request, "core/dashboard.html", {
        "recent_documents": recent_docs,
        "recent_projects": recent_projects,
    })

class DocumentAccessListView(LoginRequiredMixin, ListView):
    """
    Reusable base class for listing documents a user can access.
    Intended for subclassing or mixin-style reuse.
    """
    model = Document
    template_name = "documents/document_list.html"
    context_object_name = "documents"

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        return [doc for doc in qs if has_document_role(user, doc, "commenter")]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_roles"] = {
            doc.id: get_user_document_role(self.request.user, doc)
            for doc in context["documents"]
        }
        return context

def home(request):
    return render(request, "home.html")

def permission_denied_view(request, exception):
    return render(request, "403.html", status=403)

def not_found_view(request, exception):
    return render(request, "404.html", status=404)
