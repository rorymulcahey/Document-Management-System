# users/admin.py

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


# Register the built-in User model using the default UserAdmin
# admin.site.register(User, UserAdmin)

# If using a custom user model later, swap in CustomUser and customize admin class
# from .models import CustomUser
# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     ...
