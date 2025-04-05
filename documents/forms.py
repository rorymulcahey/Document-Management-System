# documents/forms.py

from django import forms
from documents.models import Document, DocumentVersion, Comment
from core.permissions import can_edit_document, can_comment_on_document


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

        if document:
            self.fields['version_number'] = forms.IntegerField(
                initial=(document.latest_version().version_number + 1 if document.latest_version() else 1),
                widget=forms.HiddenInput()
            )

    def clean(self):
        cleaned = super().clean()
        if not can_edit_document(self.user, self.document):
            raise forms.ValidationError("You do not have permission to upload a new version.")
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.document = self.document
        instance.uploaded_by = self.user
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
