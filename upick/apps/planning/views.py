from django.contrib import messages

def get_user_group(request):
    """Get the user's active group or return None if user has no groups.
    Also adds an error message if the user has no groups.
    """
    if not request.user.groups.exists():
        messages.error(request, 'You must be a member of at least one group to perform this action. Please contact your administrator.')
        return None
    return request.user.groups.first()
