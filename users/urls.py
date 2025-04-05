# users/urls.py

from django.urls import path
from users import views

app_name = "users"

urlpatterns = [
    path("", views.user_list, name="list"),
    path("<str:username>/", views.user_profile, name="profile"),
]
