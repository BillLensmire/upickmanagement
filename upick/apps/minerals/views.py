from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import MineralNutrient, PlantNutrientRequirement, NutrientNote, MineralUrl
from .forms import MineralNutrientForm, PlantNutrientRequirementForm, NutrientNoteForm, MineralUrlForm

# Mineral Nutrient Views
class MineralNutrientListView(LoginRequiredMixin, ListView):
    model = MineralNutrient
    template_name = 'minerals/mineral_list.html'
    context_object_name = 'minerals'
    ordering = ['name']

class MineralNutrientDetailView(LoginRequiredMixin, DetailView):
    model = MineralNutrient
    template_name = 'minerals/mineral_detail.html'
    context_object_name = 'mineral'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plant_requirements'] = self.object.plant_requirements.all()
        context['notes'] = self.object.notes.all()
        context['urls'] = self.object.urls.all()
        return context

class MineralNutrientCreateView(LoginRequiredMixin, CreateView):
    model = MineralNutrient
    form_class = MineralNutrientForm
    template_name = 'minerals/mineral_form.html'
    success_url = reverse_lazy('minerals:mineral_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Mineral nutrient created successfully!')
        return super().form_valid(form)

class MineralNutrientUpdateView(LoginRequiredMixin, UpdateView):
    model = MineralNutrient
    form_class = MineralNutrientForm
    template_name = 'minerals/mineral_form.html'
    
    def get_success_url(self):
        return reverse_lazy('minerals:mineral_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Mineral nutrient updated successfully!')
        return super().form_valid(form)

class MineralNutrientDeleteView(LoginRequiredMixin, DeleteView):
    model = MineralNutrient
    template_name = 'minerals/mineral_confirm_delete.html'
    success_url = reverse_lazy('minerals:mineral_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Mineral nutrient deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Plant Nutrient Requirement Views
class PlantNutrientRequirementListView(LoginRequiredMixin, ListView):
    model = PlantNutrientRequirement
    template_name = 'minerals/plant_requirement_list.html'
    context_object_name = 'requirements'
    ordering = ['plant_type', 'nutrient__name']

class PlantNutrientRequirementDetailView(LoginRequiredMixin, DetailView):
    model = PlantNutrientRequirement
    template_name = 'minerals/plant_requirement_detail.html'
    context_object_name = 'requirement'

class PlantNutrientRequirementCreateView(LoginRequiredMixin, CreateView):
    model = PlantNutrientRequirement
    form_class = PlantNutrientRequirementForm
    template_name = 'minerals/plant_requirement_form.html'
    success_url = reverse_lazy('minerals:plant_requirement_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Plant nutrient requirement created successfully!')
        return super().form_valid(form)

class PlantNutrientRequirementUpdateView(LoginRequiredMixin, UpdateView):
    model = PlantNutrientRequirement
    form_class = PlantNutrientRequirementForm
    template_name = 'minerals/plant_requirement_form.html'
    
    def get_success_url(self):
        return reverse_lazy('minerals:plant_requirement_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Plant nutrient requirement updated successfully!')
        return super().form_valid(form)

class PlantNutrientRequirementDeleteView(LoginRequiredMixin, DeleteView):
    model = PlantNutrientRequirement
    template_name = 'minerals/plant_requirement_confirm_delete.html'
    success_url = reverse_lazy('minerals:plant_requirement_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Plant nutrient requirement deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Nutrient Note Views
class NutrientNoteListView(LoginRequiredMixin, ListView):
    model = NutrientNote
    template_name = 'minerals/nutrient_note_list.html'
    context_object_name = 'notes'
    ordering = ['-created_at']

class NutrientNoteDetailView(LoginRequiredMixin, DetailView):
    model = NutrientNote
    template_name = 'minerals/nutrient_note_detail.html'
    context_object_name = 'note'

class NutrientNoteCreateView(LoginRequiredMixin, CreateView):
    model = NutrientNote
    form_class = NutrientNoteForm
    template_name = 'minerals/nutrient_note_form.html'
    success_url = reverse_lazy('minerals:nutrient_note_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Nutrient note created successfully!')
        return super().form_valid(form)

class NutrientNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = NutrientNote
    form_class = NutrientNoteForm
    template_name = 'minerals/nutrient_note_form.html'
    
    def get_success_url(self):
        return reverse_lazy('minerals:nutrient_note_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Nutrient note updated successfully!')
        return super().form_valid(form)

class NutrientNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = NutrientNote
    template_name = 'minerals/nutrient_note_confirm_delete.html'
    success_url = reverse_lazy('minerals:nutrient_note_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Nutrient note deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Mineral URL Views
class MineralUrlListView(LoginRequiredMixin, ListView):
    model = MineralUrl
    template_name = 'minerals/url_list.html'
    context_object_name = 'urls'
    ordering = ['-created_at']

class MineralUrlDetailView(LoginRequiredMixin, DetailView):
    model = MineralUrl
    template_name = 'minerals/url_detail.html'
    context_object_name = 'url_obj'

class MineralUrlCreateView(LoginRequiredMixin, CreateView):
    model = MineralUrl
    form_class = MineralUrlForm
    template_name = 'minerals/url_form.html'
    success_url = reverse_lazy('minerals:url_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Mineral URL created successfully!')
        return super().form_valid(form)

class MineralUrlUpdateView(LoginRequiredMixin, UpdateView):
    model = MineralUrl
    form_class = MineralUrlForm
    template_name = 'minerals/url_form.html'
    
    def get_success_url(self):
        return reverse_lazy('minerals:mineral_url_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Mineral URL updated successfully!')
        return super().form_valid(form)

class MineralUrlDeleteView(LoginRequiredMixin, DeleteView):
    model = MineralUrl
    template_name = 'minerals/url_confirm_delete.html'
    success_url = reverse_lazy('minerals:url_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Mineral URL deleted successfully!')
        return super().delete(request, *args, **kwargs)
