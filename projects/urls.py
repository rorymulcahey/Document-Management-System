# projects/urls.py

from django.urls import path
from projects import views

app_name = "projects"

urlpatterns = [
    path("", views.project_list, name="list"),
    path("<int:project_id>/", views.project_detail, name="detail"),
    path('create/', views.create_project, name='create'),
    path("<int:project_id>/edit/", views.edit_project, name="edit"),
    path("<int:project_id>/share/", views.manage_access, name="share"),
    path("<int:project_id>/delete/", views.delete_project, name="delete"),
]
