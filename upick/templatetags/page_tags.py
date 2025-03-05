from django import template
from django.template.defaultfilters import slugify

register = template.Library()

@register.simple_tag
def page_id(app_name, template_name, action=None):
    """Generate a unique page ID based on app, template, and action."""
    parts = [app_name, template_name]
    if action:
        parts.append(action)
    return f"page-{slugify('-'.join(parts))}"
