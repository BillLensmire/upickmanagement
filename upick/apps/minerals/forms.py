from django import forms
from django.forms import ModelForm
from django.utils.html import format_html
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML, Field

from .models import MineralNutrient, PlantNutrientRequirement, NutrientNote, MineralUrl

class MineralNutrientForm(ModelForm):
    class Meta:
        model = MineralNutrient
        fields = [
            'name', 'symbol', 'category', 'description',
            'function', 'deficiency_symptoms', 'excess_symptoms',
            'optimal_soil_ph', 'sources', 'application_methods',
            'application_rate', 'interactions'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'symbol': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'function': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'deficiency_symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'excess_symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'optimal_soil_ph': forms.TextInput(attrs={'class': 'form-control'}),
            'sources': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'application_methods': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'application_rate': forms.TextInput(attrs={'class': 'form-control'}),
            'interactions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6'),
                Column('symbol', css_class='col-md-2'),
                Column('category', css_class='col-md-4'),
                css_class='form-row'
            ),
            'description',
            HTML("<h4 class='mt-4'>Plant Health Information</h4><hr>"),
            'function',
            Row(
                Column('deficiency_symptoms', css_class='col-md-6'),
                Column('excess_symptoms', css_class='col-md-6'),
                css_class='form-row'
            ),
            HTML("<h4 class='mt-4'>Soil and Application Information</h4><hr>"),
            Row(
                Column('optimal_soil_ph', css_class='col-md-4'),
                Column('application_rate', css_class='col-md-8'),
                css_class='form-row'
            ),
            'sources',
            'application_methods',
            HTML("<h4 class='mt-4'>Interactions</h4><hr>"),
            'interactions',
            Submit('submit', 'Save', css_class='btn btn-success mt-3')
        )

class PlantNutrientRequirementForm(ModelForm):
    class Meta:
        model = PlantNutrientRequirement
        fields = ['plant_type', 'nutrient', 'requirement_level', 'critical_points_of_influence', 'notes']
        widgets = {
            'plant_type': forms.TextInput(attrs={'class': 'form-control'}),
            'nutrient': forms.Select(attrs={'class': 'form-select'}),
            'requirement_level': forms.Select(attrs={'class': 'form-select'}),
            'critical_points_of_influence': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('plant_type', css_class='col-md-6'),
                Column('nutrient', css_class='col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('requirement_level', css_class='col-md-6'),
                Column('critical_points_of_influence', css_class='col-md-6'),
                css_class='form-row'
            ),
            'notes',
            Submit('submit', 'Save', css_class='btn btn-success mt-3')
        )

class NutrientNoteForm(ModelForm):
    class Meta:
        model = NutrientNote
        fields = ['title', 'nutrient', 'content', 'source']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'nutrient': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        help_texts = {
            'content': 'Enter your notes here. You can use Markdown and LaTeX formatting.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.urls import reverse_lazy
        self.fields['content'].help_text = format_html('Enter your notes here. <a href="{}" target="_blank">Learn more about formatting</a>', reverse_lazy('help:markdown_latex_help'))
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='col-md-8'),
                Column('nutrient', css_class='col-md-4'),
                css_class='form-row'
            ),
            'content',
            Row(
                Column('source', css_class='col-md-6'),
                Column('url', css_class='col-md-6'),
                css_class='form-row'
            ),
            Submit('submit', 'Save', css_class='btn btn-success mt-3')
        )

class MineralUrlForm(ModelForm):
    class Meta:
        model = MineralUrl
        fields = ['mineral', 'url']
        widgets = {
            'mineral': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'mineral',
            'url',
            Submit('submit', 'Save', css_class='btn btn-success mt-3')
        )
