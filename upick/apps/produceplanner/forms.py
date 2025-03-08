from django import forms
from .models import ProducePlanOverview, ProducePlan, Plant, Variety
from django.contrib.auth.models import Group

class ProducePlanOverviewForm(forms.ModelForm):

    class Meta:
        model = ProducePlanOverview
        fields = ['name', 'year', 'overall_start_date', 'overall_end_date']
        widgets = {
            'overall_start_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'autocomplete': 'off'
            }),
            'overall_end_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'autocomplete': 'off'
            }),
        }

class ProducePlanForm(forms.ModelForm):
    
    class Meta:
        model = ProducePlan
        fields = ['plant', 'produce_plan_overview', 'variety']
        widgets = {
            'produce_plan_overview': forms.HiddenInput(),
            'plant': forms.Select(attrs={'class': 'form-select'}),
            'variety': forms.Select(attrs={'class': 'form-select'}),
        }