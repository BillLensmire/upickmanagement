from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q
from .models import Plant, Variety

# Create your views here.

def get_user_group(request):
    """Get the user's active group or return None if user has no groups.
    Also adds an error message if the user has no groups.
    """
    if not request.user.groups.exists():
        messages.error(request, 'You must be a member of at least one group to perform this action. Please contact your administrator.')
        return None
    return request.user.groups.first()

class PlantListView(ListView):
    model = Plant
    template_name = 'plants/plant_list.html'
    context_object_name = 'plants'

    def get_queryset(self):
        return Plant.objects.filter(group__in=self.request.user.groups.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seed_types'] = dict(Plant._meta.get_field('seed_type').choices)
        context['page_app'] = 'plants'
        context['page_name'] = 'plant'
        context['page_action'] = 'list'
        return context

class PlantDetailView(DetailView):
    model = Plant
    template_name = 'plants/plant_detail.html'
    context_object_name = 'plant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plant = self.get_object()
        context['companion_plants'] = plant.companion_plants.all()
        context['varieties'] = Variety.objects.filter(variety_plant=plant)
        context['page_app'] = 'plants'
        context['page_name'] = 'plant'
        context['page_action'] = 'detail'
        return context

class PlantSearchView(ListView):
    model = Plant
    template_name = 'plants/plant_list.html'
    context_object_name = 'plants'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seasons'] = dict(Plant._meta.get_field('planting_season').choices)
        context['seed_types'] = dict(Plant._meta.get_field('seed_type').choices)
        context['page_app'] = 'plants'
        context['page_name'] = 'plant'
        context['page_action'] = 'list'
        return context

    def get_queryset(self):
        queryset = Plant.objects.all()
        q = self.request.GET.get('q')
        season = self.request.GET.get('season')
        sun = self.request.GET.get('sun')
        plant_type = self.request.GET.get('type')
        
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(variety_name__icontains=q) |
                Q(scientific_name__icontains=q) |
                Q(description__icontains=q)
            )
        
        if season:
            queryset = queryset.filter(planting_season=season)
                
        if plant_type:
            queryset = queryset.filter(seed_type=plant_type)
            
        return queryset


class PlantCreateView(LoginRequiredMixin, CreateView):
    model = Plant
    template_name = 'plants/plant_form.html'
    fields = [
        'name', 'description', 'seed_type',
        'planting_method',
        'spacing_between_plants', 'spacing_between_rows',
        'germination_temp_min', 'germination_temp_max',
        'days_to_germinate', 'days_to_maturity',
        'days_from_seed_to_transplant', 'days_from_frost_to_transplant',
        'height_inches', 'is_perennial',
        'companion_plants', 'research_notes'
    ]

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.group = self.request.user.groups.first()
        if not instance.group:
            messages.error(self.request, 'You must be a member of at least one group to create a plant.')
            return self.form_invalid(form)
        instance.save()
        messages.success(self.request, 'Plant created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('plants:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'plants'
        context['page_name'] = 'plant'
        context['page_action'] = 'form'
        context['groups'] = get_user_group(self.request)
        return context


class PlantUpdateView(LoginRequiredMixin, UpdateView):
    model = Plant
    template_name = 'plants/plant_form.html'
    fields = [
        'name', 'description', 'seed_type',
        'planting_method',
        'spacing_between_plants', 'spacing_between_rows',
        'germination_temp_min', 'germination_temp_max',
        'days_to_germinate', 'days_to_maturity',
        'days_from_seed_to_transplant', 'days_from_frost_to_transplant',
        'height_inches', 'is_perennial',
        'companion_plants', 'research_notes'
    ]

    def get_success_url(self):
        return reverse_lazy('plants:detail', kwargs={'pk': self.object.pk})

    def get_cancel_url(self):
        return reverse_lazy('plants:detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Plant updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seed_types'] = dict(Plant._meta.get_field('seed_type').choices)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_type'] = self.request.GET.get('type', '')
        return context


class PlantDeleteView(LoginRequiredMixin, DeleteView):
    model = Plant
    success_url = reverse_lazy('plants:list')
    
    def delete(self, request, *args, **kwargs):
        plant = self.get_object()
        messages.success(request, f'Plant "{plant.name}" was deleted successfully!')
        return super().delete(request, *args, **kwargs)


class VarietyListView(ListView):
    model = Variety
    template_name = 'plants/variety_list.html'
    context_object_name = 'varieties'

    def get_queryset(self):
        return Variety.objects.filter(group__in=self.request.user.groups.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plant_list'] = Plant.objects.filter(group__in=self.request.user.groups.all())
        context['page_app'] = 'plants'
        context['page_name'] = 'variety'
        context['page_action'] = 'list'
        return context

class VarietyDetailView(DetailView):
    model = Variety
    template_name = 'plants/variety_detail.html'
    context_object_name = 'variety'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'plants'
        context['page_name'] = 'variety'
        context['page_action'] = 'detail'
        return context

class VarietySearchView(ListView):
    model = Variety
    template_name = 'plants/variety_list.html'
    context_object_name = 'varieties'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'plants'
        context['page_name'] = 'variety'
        context['page_action'] = 'list'
        return context

    def get_queryset(self):
        queryset = Variety.objects.all()
        q = self.request.GET.get('q')
        plant = self.request.GET.get('plant')
        
        if q:
            queryset = queryset.filter(
                Q(variety_name__icontains=q) |
                Q(scientific_name__icontains=q) |
                Q(variety_description__icontains=q)
            )
        
        if plant:
            queryset = queryset.filter(variety_plant_id=plant)
            
        return queryset

class VarietyCreateView(LoginRequiredMixin, CreateView):
    model = Variety
    template_name = 'plants/variety_form.html'
    fields = [
        'variety_plant', 'variety_name', 'scientific_name', 'variety_description',
        'variety_planting_method', 'variety_spacing_between_plants', 'variety_spacing_between_rows',
        'variety_days_to_maturity', 'variety_days_from_seed_to_transplant',
        'variety_days_from_frost_to_transplant', 'variety_planting_season'
    ]
    success_url = reverse_lazy('plants:variety_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'plants'
        context['page_name'] = 'variety'
        context['page_action'] = 'create' if not self.object else 'update'
        return context

    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            messages.error(self.request, 'You must be a member of at least one group to create a variety.')
            return redirect('plants:variety_list')
        instance = form.save(commit=False)
        instance.group = group
        instance.plant = self.get_object().variety_plant
        instance.save()
        messages.success(self.request, 'Variety created successfully!')
        return super().form_valid(form)

class VarietyUpdateView(LoginRequiredMixin, UpdateView):
    model = Variety
    template_name = 'plants/variety_form.html'
    fields = [
        'variety_plant', 'variety_name', 'scientific_name', 'variety_description',
        'variety_planting_method', 'variety_spacing_between_plants', 'variety_spacing_between_rows',
        'variety_days_to_maturity', 'variety_days_from_seed_to_transplant',
        'variety_days_from_frost_to_transplant', 'variety_planting_season'
    ]

    def get_success_url(self):
        return reverse('plants:variety_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            messages.error(self.request, 'You must be a member of at least one group to update a variety.')
            return redirect('plants:variety_list')
        instance = form.save(commit=False)
        instance.group = group
        instance.plant = self.get_object().variety_plant
        instance.save()
        messages.success(self.request, f'Variety "{form.instance.variety_name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'plants'
        context['page_name'] = 'variety'
        context['page_action'] = 'update'
        return context

class VarietyDeleteView(LoginRequiredMixin, DeleteView):
    model = Variety
    success_url = reverse_lazy('plants:variety_list')

    def delete(self, request, *args, **kwargs):
        variety = self.get_object()
        messages.success(request, f'Variety "{variety.variety_name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)

class PlantVarietyCreateView(LoginRequiredMixin, CreateView):
    model = Variety
    template_name = 'plants/variety_form.html'
    fields = [
        'variety_name', 'scientific_name', 'variety_description',
        'variety_planting_method', 'variety_spacing_between_plants', 'variety_spacing_between_rows',
        'variety_days_to_maturity', 'variety_days_from_seed_to_transplant',
        'variety_days_from_frost_to_transplant', 'variety_planting_season'
    ]
    
    def get_success_url(self):
        return reverse_lazy('plants:detail', kwargs={'pk': self.kwargs['plant_pk']})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        plant = get_object_or_404(Plant, pk=self.kwargs['plant_pk'])
        
        # Pre-populate form fields with values from the parent plant
        form.initial['variety_planting_method'] = plant.planting_method
        form.initial['variety_spacing_between_plants'] = plant.spacing_between_plants
        form.initial['variety_spacing_between_rows'] = plant.spacing_between_rows
        form.initial['variety_days_to_maturity'] = plant.days_to_maturity
        form.initial['variety_days_from_seed_to_transplant'] = plant.days_from_seed_to_transplant
        form.initial['variety_days_from_frost_to_transplant'] = plant.days_from_frost_to_transplant
        
        return form
    
    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            messages.error(self.request, 'You must be a member of at least one group to create a variety.')
            return redirect('plants:variety_list')
        instance = form.save(commit=False)
        instance.group = group
        instance.variety_plant = get_object_or_404(Plant, pk=self.kwargs['plant_pk'])
        instance.save()
        messages.success(self.request, 'Variety added successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plant'] = get_object_or_404(Plant, pk=self.kwargs['plant_pk'])
        context['page_app'] = 'plants'
        context['page_name'] = 'variety'
        context['page_action'] = 'form'
        return context
