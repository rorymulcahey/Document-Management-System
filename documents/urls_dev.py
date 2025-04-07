# documents/urls_dev.py

from django.urls import path
from . import views_dev

# Usage:
# http://localhost:8000/dev/switch-role/1/commenter
# http://localhost:8000/dev/switch-role/1/editor
# http://localhost:8000/dev/switch-role/1/owner

urlpatterns = [
	path("switch-role/<int:project_id>/<str:role>/", views_dev.switch_role, name="switch_role"),
]
