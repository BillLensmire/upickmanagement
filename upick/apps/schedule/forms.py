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
        required=False,  # Default to False, we'll set it dynamically in __init__
        input_formats=['%m/%d/%Y', '%Y-%m-%d'],
        error_messages={'required': 'Inside planting date is required for transplant varieties.'},
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'data-date-format': 'mm/dd/yyyy',
            'placeholder': 'MM/DD/YYYY',
            'autocomplete': 'off'
        })
    )
    
    outside_planting_date = forms.DateField(
        required=True,
        input_formats=['%m/%d/%Y', '%Y-%m-%d'],
        error_messages={'required': 'Outside planting date is required.'},
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'data-date-format': 'mm/dd/yyyy',
            'placeholder': 'MM/DD/YYYY',
            'autocomplete': 'off'
        })
    )
    
    harvest_date = forms.DateField(
        required=True,
        input_formats=['%m/%d/%Y', '%Y-%m-%d'],
        error_messages={'required': 'Harvest date is required.'},
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'data-date-format': 'mm/dd/yyyy',
            'placeholder': 'MM/DD/YYYY',
            'autocomplete': 'off'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    location_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    
    class Meta:
        model = PlantingSchedule
        fields = ['garden_bed', 'variety', 'garden_plan', 'quantity', 'rows', 
                 'inside_planting_date', 'outside_planting_date', 'harvest_date', 'notes', 'location_notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
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
            
            # Make garden_plan required
            self.fields['garden_plan'].required = True
            
            # Make garden_bed required
            self.fields['garden_bed'].required = True

            # Make variety required
            self.fields['variety'].required = True
            
        # Set inside_planting_date required based on variety's planting method
        # For existing instances with a variety
        if self.instance and self.instance.pk and self.instance.variety:
            if self.instance.variety.variety_planting_method == 'TRANSPLANT':
                self.fields['inside_planting_date'].required = True
            else:
                self.fields['inside_planting_date'].required = False
            
    def clean(self):
        cleaned_data = super().clean()
        
        # Get the variety from the cleaned data
        variety = cleaned_data.get('variety')
        inside_planting_date = cleaned_data.get('inside_planting_date')
        
        # Check if inside_planting_date is required based on variety's planting method
        if variety and variety.variety_planting_method == 'TRANSPLANT' and not inside_planting_date:
            self.add_error('inside_planting_date', 'Inside planting date is required for transplant varieties.')
            
        return cleaned_data
