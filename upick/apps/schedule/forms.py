from django import forms
from datetime import datetime
from .models import TodoTask, TodoList, PlantingSchedule, GardenBed
from django.contrib.auth.models import Group
from apps.plants.models import Variety
from apps.planning.models import GardenPlan
from django.db.models import Q

class TodoTaskForm(forms.ModelForm):
    """Form for creating and updating Todo Tasks"""
    
    # Add custom date field to handle mm/dd/yyyy format
    due_date = forms.DateField(
        required=False,
        input_formats=['%m/%d/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'data-date-format': 'mm/dd/yyyy',
            'placeholder': 'MM/DD/YYYY',
            'autocomplete': 'off'
        })
    )
    
    class Meta:
        model = TodoTask
        fields = ['title', 'description', 'due_date', 'priority', 'status', 
                  'garden_bed', 'planting_schedule', 'group']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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


class PlantingScheduleForm(forms.ModelForm):
    """Form for creating and updating Planting Schedules"""
    
    # Add custom date fields to handle mm/dd/yyyy format
    inside_planting_date = forms.DateField(
        required=False,
        input_formats=['%m/%d/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'data-date-format': 'mm/dd/yyyy',
            'placeholder': 'MM/DD/YYYY',
            'autocomplete': 'off'
        })
    )
    
    outside_planting_date = forms.DateField(
        required=False,
        input_formats=['%m/%d/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'data-date-format': 'mm/dd/yyyy',
            'placeholder': 'MM/DD/YYYY',
            'autocomplete': 'off'
        })
    )
    
    harvest_date = forms.DateField(
        required=False,
        input_formats=['%m/%d/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'data-date-format': 'mm/dd/yyyy',
            'placeholder': 'MM/DD/YYYY',
            'autocomplete': 'off'
        })
    )
    
    class Meta:
        model = PlantingSchedule
        fields = ['garden_bed', 'variety', 'garden_plan', 'quantity', 'rows', 
                 'inside_planting_date', 'outside_planting_date', 'harvest_date']
        widgets = {
            'garden_bed': forms.Select(attrs={'class': 'form-control'}),
            'variety': forms.Select(attrs={'class': 'form-control'}),
            'garden_plan': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'rows': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.selected_year = kwargs.pop('selected_year', None)
        super().__init__(*args, **kwargs)
        
        if self.request and self.request.user.groups.exists():
            # Filter garden beds by the selected year and user's groups
            self.fields['garden_bed'].queryset = GardenBed.objects.filter(
                group__in=self.request.user.groups.all(),
                year=self.selected_year
            )
            
            # Filter varieties by user's groups
            self.fields['variety'].queryset = Variety.objects.filter(
                Q(variety_plant__group__in=self.request.user.groups.all()) | Q(variety_plant__group=None)
            ).select_related('variety_plant')
            
            # Filter garden plans by the selected year and user's groups
            self.fields['garden_plan'].queryset = GardenPlan.objects.filter(
                group__in=self.request.user.groups.all(), 
                year=self.selected_year
            ).order_by('-year', 'name')
            
            # Make garden_plan optional
            self.fields['garden_plan'].required = False
