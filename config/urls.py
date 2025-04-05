import os
from django.http import Http404
from django.urls import re_path
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import dashboard
from django.contrib.auth import views as auth_views

def safe_serve(request, path, document_root=None, show_indexes=False):
    full_path = os.path.join(document_root, path)
    if not os.path.exists(full_path):
        raise Http404("Requested media file was not found.")
    return static_serve(request, path, document_root=document_root, show_indexes=show_indexes)
	
urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Users App
    path('users/', include('users.urls', namespace='users')),

    # Projects App
    path('projects/', include('projects.urls', namespace='projects')),

    # Documents App
    path('documents/', include('documents.urls', namespace='documents')),

    # Audit Log App
    path('auditlog/', include('auditlog.urls', namespace='auditlog')),

    # Home
    path("", dashboard, name="home"),

    # Add auth views for login/logout
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
]

# Serve media in dev with 404 fallback
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', safe_serve, {'document_root': settings.MEDIA_ROOT}),
    ]

handler403 = "core.views.permission_denied_view"
handler404 = "core.views.not_found_view"
