# core/access.py

from auditlog.models import ShareActionLog
from guardian.shortcuts import assign_perm, remove_perm

def update_access(actor, target_user, container, role, remove=False):
	"""
	Shared logic for managing access across Document, Project, DataRow.

	- Assigns or removes permissions
	- Logs the action to ShareActionLog
	"""
	from documents.models import Document
	from projects.models import Project

	if isinstance(container, Document):
		if remove:
			for perm in ["owner_document", "editor_document", "commenter_document"]:
				remove_perm(perm, target_user, container)
			action = "unshared"
			role_value = None
		else:
			perm_map = {
				"owner": "owner_document",
				"editor": "editor_document",
				"commenter": "commenter_document"
			}
			for perm in perm_map.values():
				remove_perm(perm, target_user, container)
			assign_perm(perm_map[role], target_user, container)
			action = "shared"  # TODO: detect role_changed
			role_value = role

		ShareActionLog.objects.create(
			actor=actor,
			target_user=target_user,
			document=container,
			role=role_value,
			action=action
		)

	elif isinstance(container, Project):
		# This branch will be activated later when we refactor projects
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
