from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from .models import Reminder
from django import forms
from django.contrib.auth.models import Group

def get_user_group(request):
    """Get the user's active group or return None if user has no groups.
    Also adds an error message if the user has no groups.
    """
    if not request.user.groups.exists():
        messages.error(request, 'You must be a member of at least one group to perform this action. Please contact your administrator.')
        return None
    return request.user.groups.first()

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['title', 'description', 'due_date', 'priority', 'assigned_to']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

@login_required
def reminder_list(request):
    # Get user's reminders
    user_reminders = Reminder.objects.filter(
        models.Q(creator=request.user) | models.Q(assigned_to=request.user)
    )
    
    # Get active reminders and group them by month
    active_reminders = user_reminders.filter(completed=False).order_by('due_date')
    grouped_reminders = {}
    
    for reminder in active_reminders:
        if reminder.due_date:
            month_key = reminder.due_date.strftime('%Y-%m')
            month_display = reminder.due_date.strftime('%B %Y')
            if month_key not in grouped_reminders:
                grouped_reminders[month_key] = {'display': month_display, 'reminders': []}
            grouped_reminders[month_key]['reminders'].append(reminder)
        else:
            if 'no_date' not in grouped_reminders:
                grouped_reminders['no_date'] = {'display': 'No Date', 'reminders': []}
            grouped_reminders['no_date']['reminders'].append(reminder)
    
    # Sort months chronologically
    sorted_months = sorted(grouped_reminders.items(), key=lambda x: x[1]['display'])
    
    # Get completed reminders
    completed_reminders = user_reminders.filter(completed=True).order_by('-updated_at')
    
    context = {
        'grouped_reminders': sorted_months,
        'completed_reminders': completed_reminders,
        'now': timezone.now(),
    }
    return render(request, 'reminders/reminder_list.html', context)

@login_required
def reminder_list_completed(request):
    # Get user's reminders
    user_reminders = Reminder.objects.filter(
        models.Q(creator=request.user) | models.Q(assigned_to=request.user)
    )
    
    # Get completed reminders
    completed_reminders = user_reminders.filter(completed=True).order_by('-updated_at')
    
    context = {
        'completed_reminders': completed_reminders,
        'now': timezone.now(),
    }
    return render(request, 'reminders/reminder_list_completed.html', context)

@login_required
def reminder_detail(request, pk):
    reminder = get_object_or_404(
        Reminder.objects.filter(
            models.Q(creator=request.user) | models.Q(assigned_to=request.user)
        ),
        pk=pk
    )
    return render(request, 'reminders/reminder_detail.html', {'reminder': reminder})

@login_required
def reminder_create(request):
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.creator = request.user
            group = get_user_group(request)
            if not group:
                form.add_error(None, 'You must be a member of at least one group to create a reminder.')
                return self.form_invalid(form)
            reminder.group = group
            reminder.save()
            messages.success(request, 'Reminder created successfully!')
            #return redirect('reminders:reminder_detail', pk=reminder.pk)
            return redirect('reminders:reminder_list')
    else:
        form = ReminderForm(initial={'assigned_to': request.user})
    
    context = {
        'form': form,
        'action': 'Create',
        'groups': Group.objects.all()
    }
    return render(request, 'reminders/reminder_form.html', context)

@login_required
def reminder_edit(request, pk):
    reminder = get_object_or_404(
        Reminder.objects.filter(creator=request.user),
        pk=pk
    )
    
    if request.method == 'POST':
        form = ReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reminder updated successfully!')
            return redirect('reminders:reminder_detail', pk=reminder.pk)
    else:
        form = ReminderForm(instance=reminder)
    
    return render(request, 'reminders/reminder_form.html', {'form': form, 'action': 'Edit'})

@login_required
def reminder_toggle_complete(request, pk):
    reminder = get_object_or_404(
        Reminder.objects.filter(
            models.Q(creator=request.user) | models.Q(assigned_to=request.user)
        ),
        pk=pk
    )
    reminder.completed = not reminder.completed
    reminder.save()
    messages.success(request, f'Reminder marked as {"completed" if reminder.completed else "incomplete"}!')
    return redirect('reminders:reminder_list')

@login_required
def reminder_duplicate(request, pk):
    original_reminder = get_object_or_404(
        Reminder.objects.filter(
            models.Q(creator=request.user) | models.Q(assigned_to=request.user)
        ),
        pk=pk
    )
    
    # Create a new reminder with the same details but not completed
    initial_data = {
        'title': original_reminder.title,
        'description': original_reminder.description,
        'priority': original_reminder.priority,
        'assigned_to': original_reminder.assigned_to,
        # Don't copy the due_date as it's likely different for the new reminder
    }
    
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.creator = request.user
            reminder.completed = False  # Ensure the new reminder is not marked as completed
            reminder.save()
            messages.success(request, 'New reminder created from existing one!')
            return redirect('reminders:reminder_detail', pk=reminder.pk)
    else:
        form = ReminderForm(initial=initial_data)
    
    return render(request, 'reminders/reminder_form.html', {
        'form': form,
        'action': 'Create',
        'title': f'New Reminder from "{original_reminder.title}"'
    })
