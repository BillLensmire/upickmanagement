from django import forms
from .models import ProducePlanOverview, ProducePlan

class ProducePlanOverviewForm(forms.ModelForm):
    class Meta:
        model = ProducePlanOverview
        fields = ['garden_plan', 'overall_start_date', 'overall_end_date']
        widgets = {
            'garden_plan': forms.Select(attrs={'class': 'form-control'}),
            'overall_start_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'autocomplete': 'off'
            }),
            'overall_end_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'autocomplete': 'off'
            }),
        }
