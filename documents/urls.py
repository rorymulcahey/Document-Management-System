# documents/urls.py

from django.conf import settings
from django.urls import path, include
from documents.views import document, share, comment
from auditlog.views import audit_log_filtered_view 
from documents.views.document import inline_update_document

app_name = "documents"

urlpatterns = [
    # Document list and detail
    path("", document.document_list, name="list"),
    path("create/", document.document_create, name="create"),
    path("<int:doc_id>/edit/", document.document_edit, name="edit"),
    path("<int:doc_id>/delete/", document.delete_document, name="delete"),
    path("<int:doc_id>/", document.document_detail, name="detail"),
    path("inline-update/<int:doc_id>/", inline_update_document, name="inline_update"),

    # Upload a new version
    path("<int:doc_id>/upload/", document.upload_version, name="upload"),

    # Share/unshare/change-role (POST only)
    path("<int:document_id>/share/", share.share_document_view, name="share"),
    path("<int:document_id>/unshare/", share.unshare_document_view, name="unshare"),
    path("<int:document_id>/change-role/", share.change_role_view, name="change_role"),

    # Comments
    path("<int:document_id>/comment/", comment.post_comment, name="comment"),

]

if settings.DEBUG:
	urlpatterns += [
		path("dev/", include("documents.urls_dev")),
	]
	