# core/forms.py

from django import forms


class BaseForm(forms.Form):
    """
    Hookable base form for enforcing patterns later.
    Currently a placeholder for standardization.
    """
    def clean(self):
        cleaned = super().clean()
        # Example future logic:
        # if hasattr(self, 'user') and not self.user.is_authenticated:
        #     raise forms.ValidationError("Auth required.")
        return cleaned
