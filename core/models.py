# core/models.py

from django.db import models
from django.contrib.auth.models import User


class TimeStampedModel(models.Model):
    """
    Adds created_at and updated_at fields to inheriting models.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserStampedModel(models.Model):
    """
    Adds created_by and modified_by fields.
    Extend only if you're handling ownership/creator info.
    """
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="%(class)s_created")
    modified_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="%(class)s_modified")

    class Meta:
        abstract = True
