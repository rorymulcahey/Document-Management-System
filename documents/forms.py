# documents/forms.py

from django import forms
from documents.models import Document, DocumentVersion, Comment
from core.permissions import can_edit_document, can_comment_on_document
from storage.factory import get_storage_backend


class DocumentUploadForm(forms.ModelForm):
	"""
	Uploads a new version of an existing document.
	Requires user to have edit or higher role.
	"""
	class Meta:
		model = DocumentVersion
		fields = ['file', 'notes']

	def __init__(self, *args, user=None, document=None, **kwargs):
		super().__init__(*args, **kwargs)
		self.user = user
		self.document = document
		self.storage = get_storage_backend()

	def clean(self):
		cleaned = super().clean()
		if not can_edit_document(self.user, self.document):
			raise forms.ValidationError("You do not have permission to upload a new version.")
		return cleaned

	def save(self, commit=True):
		instance = super().save(commit=False)
		instance.document = self.document
		instance.uploaded_by = self.user

		# 🧠 Calculate and set the version number BEFORE saving
		latest = self.document.versions.order_by('-version_number').first()
		instance.version_number = latest.version_number + 1 if latest else 1

		# 🎯 Save the file using storage backend
		file = self.cleaned_data['file']
		file_path = f"documents/{self.document.id}/versions/{instance.version_number}/{file.name}"
		instance.file = self.storage.save(file, file_path)

		if commit:
			instance.save()

		return instance


class CommentForm(forms.ModelForm):
	"""
	Creates a comment on a document (optionally tied to a specific version).
	"""
	class Meta:
		model = Comment
		fields = ['body', 'version']

	def __init__(self, *args, user=None, document=None, **kwargs):
		super().__init__(*args, **kwargs)
		self.user = user
		self.document = document

		if document:
			self.fields['version'].queryset = document.versions.all()

	def clean(self):
		cleaned = super().clean()
		if not can_comment_on_document(self.user, self.document):
			raise forms.ValidationError("You do not have permission to comment on this document.")
		return cleaned

	def save(self, commit=True):
		instance = super().save(commit=False)
		instance.user = self.user
		instance.document = self.document
		if commit:
			instance.save()
		return instance


class DocumentForm(forms.ModelForm):
	class Meta:
		model = Document
		fields = ["title", "description", "project"]


class InitialDocumentUploadForm(forms.ModelForm):
	"""
	Form to create a new Document and its first version.
	"""
	file = forms.FileField(label="Upload File")

	class Meta:
		model = Document
		fields = ['title', 'description', 'project']

	def __init__(self, *args, user=None, **kwargs):
		super().__init__(*args, **kwargs)
		self.user = user
		self.storage = get_storage_backend()

	def save(self, commit=True):
		document = super().save(commit=False)
		document.created_by = self.user
		if commit:
			document.save()
			file = self.cleaned_data['file']
			file_path = f"documents/{document.id}/versions/1/{file.name}"
			stored_file_path = self.storage.save(file, file_path)
			DocumentVersion.objects.create(
				document=document,
				version_number=1,
				file=stored_file_path,
				notes="Initial upload",
				uploaded_by=self.user
			)
		return document

