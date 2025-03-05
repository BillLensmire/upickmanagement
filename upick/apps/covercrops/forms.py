from django import forms
from django.forms import inlineformset_factory
from .models import CoverCropMix, CoverCropPlantComponent, CoverCropPlan

class CoverCropMixForm(forms.ModelForm):
    class Meta:
        model = CoverCropMix
        fields = ['name', 'description']

class CoverCropPlantComponentForm(forms.ModelForm):
    class Meta:
        model = CoverCropPlantComponent
        fields = ['seed_inventory', 'seeding_rate', 'percentage_in_mix']
        widgets = {
            'seeding_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'percentage_in_mix': forms.NumberInput(attrs={'min': '1', 'max': '100'})
        }

class CoverCropPlanForm(forms.ModelForm):
    class Meta:
        model = CoverCropPlan
        fields = [
            'name', 'description', 'mix',
            'planting_season', 'planting_window_start', 'planting_window_end',
            'weeks_to_grow', 'minimum_soil_temp', 'frost_tolerant',
            'drought_tolerant', 'nitrogen_fixer', 'biomass_producer',
            'weed_suppressor', 'erosion_controller', 'beneficial_insect',
            'attracted_beneficials', 'termination_method', 'days_before_cash_crop'
        ]
        widgets = {
            'planting_window_start': forms.DateInput(attrs={'type': 'date'}),
            'planting_window_end': forms.DateInput(attrs={'type': 'date'}),
            'weeks_to_grow': forms.NumberInput(attrs={'min': '1'}),
            'minimum_soil_temp': forms.NumberInput(attrs={'min': '0'}),
            'days_before_cash_crop': forms.NumberInput(attrs={'min': '0'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'attracted_beneficials': forms.SelectMultiple(attrs={'class': 'form-control'})
        }

# Create a formset for managing multiple components
CoverCropComponentFormSet = inlineformset_factory(
    CoverCropMix,
    CoverCropPlantComponent,
    form=CoverCropPlantComponentForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)
