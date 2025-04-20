# core/access.py

from auditlog.models import ShareActionLog
from guardian.shortcuts import get_perms, assign_perm, remove_perm
from projects.models import ProjectMembership

def update_access(actor, target_user, container, role, remove=False):
	"""
	Shared logic for managing access across Document, Project, DataRow.

	- Assigns or removes permissions
	- Logs the action to ShareActionLog
	"""
	from documents.models import Document
	from projects.models import Project

	if isinstance(container, Document):
		if not remove:
			is_member = ProjectMembership.objects.filter(
				project=container.project,
				user=target_user
			).exists()
			if not is_member:
				return {"success": False, "error": "User must be a project member to receive document access"}

		if remove:
			current_perms = get_perms(target_user, container)
			if current_perms:
				for perm in ["owner_document", "editor_document", "commenter_document"]:
					remove_perm(perm, target_user, container)
				ShareActionLog.objects.create(
					actor=actor,
					target_user=target_user,
					document=container,
					project=container.project,
					role=None,
					action="unshared"
				)
				return {"success": True, "removed": True, "username": target_user.username}
			else:
				return {"success": False, "error": "User had no permissions"}
		
		else:
			perm_map = {
				"owner": "owner_document",
				"editor": "editor_document",
				"commenter": "commenter_document"
			}
			for perm in perm_map.values():
				remove_perm(perm, target_user, container)
			assign_perm(perm_map[role], target_user, container)

			ShareActionLog.objects.create(
				actor=actor,
				target_user=target_user,
				document=container,
				project=container.project,
				role=role,
				action="shared"  # TODO: upgrade to "role_changed" if already had perms
			)

			return {"success": True, "role": role, "username": target_user.username}

	elif isinstance(container, Project):
		# Not implemented yet
		pass


# usage
# 
# {% include "includes/access_modal.html" with object_type="document" object_id=document.id %}
# 
# 
# context["access_modal_config"] = {
# 	"post_url": reverse("documents:update_access", args=[doc.id]),
# 	"current_roles": current_roles,
# 	"all_users": all_users
# }
