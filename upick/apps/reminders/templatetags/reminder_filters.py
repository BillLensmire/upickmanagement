from django import template

register = template.Library()

@register.filter
def filter_completed(reminders, completed=True):
    """Filter reminders by completion status."""
    return [r for r in reminders if r.completed == completed]
