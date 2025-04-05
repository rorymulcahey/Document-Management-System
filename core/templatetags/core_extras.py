# core/templatetags/core_extras.py

from django import template
register = template.Library()

@register.filter
def dict_get(d, key):
    return d.get(key) if isinstance(d, dict) else None

@register.filter
def add_class(field, css_class):
	return field.as_widget(attrs={**field.field.widget.attrs, "class": css_class})
