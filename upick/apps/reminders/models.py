from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import Group

class Reminder(models.Model): 
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_reminders',
        null=True,  # Temporarily allow null for migration
    )
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this reminder belongs to'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_reminders',
        null=True,  # Temporarily allow null for migration
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    priority = models.IntegerField(
        choices=[
            (1, 'High'),
            (2, 'Medium'),
            (3, 'Low')
        ],
        default=2
    )

    class Meta:
        ordering = ['due_date', 'priority', '-created_at']

    def __str__(self):
        return self.title

    def is_overdue(self):
        if self.due_date and not self.completed:
            return timezone.now().date() > self.due_date
        return False

    @staticmethod
    def get_available_users(user):
        """Get all users that share any group with the given user."""
        if not user.is_authenticated:
            return get_user_model().objects.none()
        
        # Get all groups the user belongs to
        user_groups = user.groups.all()
        # Get all users that belong to any of these groups
        available_users = get_user_model().objects.filter(groups__in=user_groups).distinct()
        return available_users

    def save(self, *args, **kwargs):
        # If this is a new reminder and assigned_to is not set,
        # default to the creator
        if not self.pk and not hasattr(self, 'assigned_to'):
            self.assigned_to = self.creator
        super().save(*args, **kwargs)
