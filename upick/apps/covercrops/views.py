from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView
)
from django.views.generic.edit import CreateView, UpdateView
from .models import CoverCropMix, CoverCropPlan
from .forms import CoverCropMixForm, CoverCropComponentFormSet, CoverCropPlanForm

class CoverCropMixListView(LoginRequiredMixin, ListView):
    model = CoverCropMix
    paginate_by = 12

    def get_queryset(self):
        return CoverCropMix.objects.filter(group__in=self.request.user.groups.all())

from django.db.models import Sum

class CoverCropMixDetailView(LoginRequiredMixin, DetailView):
    model = CoverCropMix

    def get_queryset(self):
        return CoverCropMix.objects.filter(group__in=self.request.user.groups.all())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        components = self.object.covercropplantcomponent_set.all()
        context['total_seeding_rate'] = sum(float(c.seeding_rate) for c in components)
        context['total_percentage'] = sum(c.percentage_in_mix for c in components)
        # Add related cover crop plans
        context['plans'] = CoverCropPlan.objects.filter(mix=self.object)
        return context

class CoverCropPlanListView(LoginRequiredMixin, ListView):
    model = CoverCropPlan
    paginate_by = 12
    
    def get_queryset(self):
        return CoverCropPlan.objects.filter(group__in=self.request.user.groups.all())

class CoverCropPlanDetailView(LoginRequiredMixin, DetailView):
    model = CoverCropPlan

    def get_queryset(self):
        return CoverCropPlan.objects.filter(group__in=self.request.user.groups.all())

class CoverCropPlanCreateView(LoginRequiredMixin, CreateView):
    model = CoverCropPlan
    form_class = CoverCropPlanForm
    
    def form_valid(self, form):
        form.instance.group = self.request.user.groups.first()
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['mix'].queryset = CoverCropMix.objects.filter(
            group__in=self.request.user.groups.all()
        )
        return form

class CoverCropPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = CoverCropPlan
    form_class = CoverCropPlanForm
    
    def get_queryset(self):
        return CoverCropPlan.objects.filter(group__in=self.request.user.groups.all())
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['mix'].queryset = CoverCropMix.objects.filter(
            group__in=self.request.user.groups.all()
        )
        return form

class CoverCropPlanDeleteView(LoginRequiredMixin, DeleteView):
    model = CoverCropPlan
    success_url = reverse_lazy('covercrops:plan_list')
    
    def get_queryset(self):
        return CoverCropPlan.objects.filter(group__in=self.request.user.groups.all())

class CoverCropMixCreateView(LoginRequiredMixin, CreateView):
    model = CoverCropMix
    form_class = CoverCropMixForm
    success_url = reverse_lazy('covercrops:mix_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['component_formset'] = CoverCropComponentFormSet(self.request.POST)
        else:
            context['component_formset'] = CoverCropComponentFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        component_formset = context['component_formset']
        
        if component_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.group = self.request.user.groups.first()
            self.object.save()
            
            component_formset.instance = self.object
            component_formset.save()
            
            messages.success(self.request, f'Cover crop mix "{self.object.name}" created successfully!')
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class CoverCropMixUpdateView(LoginRequiredMixin, UpdateView):
    model = CoverCropMix
    form_class = CoverCropMixForm
    success_url = reverse_lazy('covercrops:mix_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['component_formset'] = CoverCropComponentFormSet(
                self.request.POST, instance=self.object)
        else:
            context['component_formset'] = CoverCropComponentFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        component_formset = context['component_formset']
        
        if component_formset.is_valid():
            self.object = form.save()
            component_formset.instance = self.object
            component_formset.save()
            
            messages.success(self.request, f'Cover crop mix "{self.object.name}" updated successfully!')
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_queryset(self):
        return CoverCropMix.objects.filter(group__in=self.request.user.groups.all())

class CoverCropMixDeleteView(LoginRequiredMixin, DeleteView):
    model = CoverCropMix
    success_url = reverse_lazy('covercrops:mix_list')

    def get_queryset(self):
        return CoverCropMix.objects.filter(group__in=self.request.user.groups.all())

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f'Cover crop mix "{obj.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)
