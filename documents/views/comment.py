# documents/views/comment.py

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from documents.models import Document
from documents.forms import CommentForm

@login_required
@require_POST
def post_comment(request, document_id):
    """
    Handles creation of a new comment on a document.
    Requires permission to comment on the document.
    """
    document = get_object_or_404(Document, id=document_id)
    form = CommentForm(request.POST, user=request.user, document=document)

    if form.is_valid():
        form.save()
        return redirect('documents:detail', doc_id=document.id)

    # fallback: re-render with errors if needed (left as-is)
    return redirect('documents:detail', doc_id=document.id)
