from django import forms
from .models import TodoTask, TodoList
from django.contrib.auth.models import Group

class TodoTaskForm(forms.ModelForm):
    """Form for creating and updating Todo Tasks"""
    
    class Meta:
        model = TodoTask
        fields = ['title', 'description', 'due_date', 'priority', 'status', 
                  'garden_bed', 'planting_schedule', 'group']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'garden_bed': forms.Select(attrs={'class': 'form-control'}),
            'planting_schedule': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
        }


class TodoListForm(forms.ModelForm):
    """Form for creating and updating Todo Lists"""
    
    class Meta:
        model = TodoList
        fields = ['title', 'description', 'tasks', 'group']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tasks': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
        }
