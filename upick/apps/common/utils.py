from django.contrib.auth.models import Group

def get_default_group():
    """Temporary function to maintain migration compatibility.
    Returns None since we no longer want to auto-create groups.
    """
    return None
