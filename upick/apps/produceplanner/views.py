from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import Group
from datetime import timedelta, datetime
from .models import ProducePlanOverview, ProducePlan, Plant
from apps.plants.models import Plant, Variety
from apps.planning.models import GardenConfiguration
from .forms import ProducePlanOverviewForm, ProducePlanForm

def get_user_group(request):
    """Get the user's active group or return None if user has no groups.
    Also adds an error message if the user has no groups.
    """
    if not request.user.groups.exists():
        messages.error(request, 'You must be a member of at least one group to perform this action. Please contact your administrator.')
        return None
    return request.user.groups.first()

@login_required
def produce_availability_report(request, overview_id):
    overview = get_object_or_404(ProducePlanOverview, id=overview_id, group__in=request.user.groups.all())
    # Get only plants that have entries in this produce plan overview
    plants_with_produce_plans = Plant.objects.filter(produceplan__produce_plan_overview=overview).distinct()
    produce_plans = ProducePlan.objects.filter(produce_plan_overview=overview)

    # Find the first Sunday before or on the start date
    start_date = overview.overall_start_date
    days_to_sunday = start_date.weekday() + 1  # weekday() returns 0-6 (Mon-Sun), so add 1 to get days until previous Sunday
    if days_to_sunday < 7:  # Only adjust if we're not already on a Sunday
        start_date = start_date - timedelta(days=days_to_sunday)

    # Generate weeks until we pass the end date
    date_ranges = []
    current_date = start_date
    while current_date <= overview.overall_end_date:
        week_end = current_date + timedelta(days=6)  # Saturday
        date_ranges.append({
            'date': current_date,
            'date_range': f"{current_date.strftime('%b %d')} - {week_end.strftime('%b %d')}"
        })
        current_date += timedelta(days=7)  # Move to next Sunday

    # Create a matrix with plants/varieties as rows and weeks as columns
    plant_matrix = []
    
    # First add plants without varieties
    for plant in plants_with_produce_plans:
        # Check if this plant has varieties with produce plans
        plant_varieties = Variety.objects.filter(variety_plant=plant)
        varieties_with_plans = False
        
        for variety in plant_varieties:
            # Check if any produce plans exist for this variety
            variety_plans_exist = produce_plans.filter(
                plant=plant,
                variety=variety
            ).exists()
            
            if variety_plans_exist:
                varieties_with_plans = True
                break
        
        # If this plant has no varieties with plans, or no varieties at all, add it as a standalone plant
        if not varieties_with_plans:
            row = {
                'plant': plant.name,
                'plant_id': plant.id,
                'variety_id': None,
                'availability': []
            }

            # For each week, check if the plant is available
            for week in date_ranges:
                is_available = produce_plans.filter(
                    plant=plant,
                    variety__isnull=True
                ).exists()
                row['availability'].append(is_available)

            plant_matrix.append(row)
    
    # Now add plants with varieties
    for plant in plants_with_produce_plans:
        plant_varieties = Variety.objects.filter(variety_plant=plant)
        
        for variety in plant_varieties:
            # Check if any produce plans exist for this variety
            variety_plans_exist = produce_plans.filter(
                plant=plant,
                variety=variety
            ).exists()
            
            if variety_plans_exist:
                row = {
                    'plant': f"{plant.name} ({variety.variety_name})",
                    'plant_id': plant.id,
                    'variety_id': variety.id,
                    'availability': []
                }

                # For each week, check if the variety is available
                for week in date_ranges:
                    is_available = produce_plans.filter(
                        plant=plant,
                        variety=variety,
                        produce_plan_overview__overall_start_date__lte=week['date'] + timedelta(days=6),
                        produce_plan_overview__overall_end_date__gte=week['date']
                    ).exists()
                    row['availability'].append(is_available)

                plant_matrix.append(row)

    context = {
        'overview': overview,
        'date_ranges': date_ranges,
        'plant_matrix': plant_matrix,
        'page_app': 'produceplanner',
        'page_name': 'report',
        'page_action': 'view'
    }
    return render(request, 'produceplanner/report.html', context)

@require_POST
def update_planting_date(request, plan_id):
    """Update the planting date for a produce plan."""
    try:
        plan = get_object_or_404(ProducePlan, id=plan_id)
        date_str = request.POST.get('planting_date')
        planting_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Update the plan's start date based on the planting date
        plan.start_date = planting_date
        plan.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Updated planting date to {planting_date}'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def get_varieties(request, pk):
    varieties = Variety.objects.filter(variety_plant=pk).order_by('variety_name')
    print("varieties", varieties)
    jresp = JsonResponse({'varieties': list(varieties.values('id', 'variety_name'))})
    print("jresp", jresp.content)
    return jresp

class ProducePlanOverviewListView(LoginRequiredMixin, ListView):
    model = ProducePlanOverview
    template_name = 'produceplanner/overview_list.html'
    context_object_name = 'overviews'

    def get_queryset(self):
        return super().get_queryset().filter(group__in=self.request.user.groups.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'produceplanner'
        context['page_name'] = 'overview'
        context['page_action'] = 'list'
        return context

class ProducePlanOverviewCreateView(LoginRequiredMixin, CreateView):
    model = ProducePlanOverview
    template_name = 'produceplanner/overview_form.html'
    form_class = ProducePlanOverviewForm
    success_url = reverse_lazy('produceplanner:overview_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form

    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a produce plan overview.')
            return self.form_invalid(form)
        instance = form.save(commit=False)
        instance.group = group
        instance.save()
        messages.success(self.request, 'Produce plan overview created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'produceplanner'
        context['page_name'] = 'overview'
        context['page_action'] = 'form'
        return context

class ProducePlanOverviewUpdateView(LoginRequiredMixin, UpdateView):
    model = ProducePlanOverview
    template_name = 'produceplanner/overview_form.html'
    form_class = ProducePlanOverviewForm
    success_url = reverse_lazy('produceplanner:overview_list')

    def get_queryset(self):
        return super().get_queryset().filter(group__in=self.request.user.groups.all())

    def form_valid(self, form):
        messages.success(self.request, 'Produce plan overview updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'produceplanner'
        context['page_name'] = 'overview'
        context['page_action'] = 'form'
        return context

class ProducePlanOverviewDetailView(LoginRequiredMixin, DetailView):
    model = ProducePlanOverview
    template_name = 'produceplanner/overview_detail.html'
    context_object_name = 'overview'

    def get_queryset(self):
        return super().get_queryset().filter(group__in=self.request.user.groups.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['produce_plans'] = self.object.produce_plans.all().select_related('plant')
        context['available_plants'] = Plant.objects.all().filter(group__in=self.request.user.groups.all())
        context['available_varieties'] = Variety.objects.all().filter(group__in=self.request.user.groups.all())
        context['page_app'] = 'produceplanner'
        context['page_name'] = 'overview'
        context['page_action'] = 'detail'
        return context

class ProducePlanCreateView(LoginRequiredMixin, CreateView):
    model = ProducePlan
    form_class = ProducePlanForm
    template_name = 'produceplanner/produceplan_form.html'
    
    def get_success_url(self):
        return reverse_lazy('produceplanner:overview_detail', kwargs={'pk': self.kwargs['overview_id']})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        overview = get_object_or_404(ProducePlanOverview, id=self.kwargs['overview_id'])
        initial['produce_plan_overview'] = overview.id
        return initial
    
    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a produce plan.')
            return self.form_invalid(form)
        
        overview = get_object_or_404(ProducePlanOverview, id=self.kwargs['overview_id'])
        instance = form.save(commit=False)
        instance.group = group
        instance.produce_plan_overview = overview
        instance.save()
        
        plant_name = instance.plant.name
        if instance.variety:
            plant_name = f"{instance.plant.name} ({instance.variety.variety_name})"
        
        messages.success(self.request, f'Added {plant_name} to the produce plan')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):

        # make a list of varieties for each plant
        plant_varieties = {}
        for plant in Plant.objects.all().order_by('name'):
            varieties = Variety.objects.filter(variety_plant=plant).order_by('variety_name')
            plant_varieties[plant.id] = varieties
        
        context = super().get_context_data(**kwargs)
        overview = get_object_or_404(ProducePlanOverview, id=self.kwargs['overview_id'])
        context['overview'] = overview
        context['available_plants'] = Plant.objects.all().order_by('name')
        context['available_varieties'] = plant_varieties
        context['page_app'] = 'produceplanner'
        context['page_name'] = 'produceplan'
        context['page_action'] = 'create'
        return context

class ProducePlanUpdateView(LoginRequiredMixin, UpdateView):
    model = ProducePlan
    form_class = ProducePlanForm
    template_name = 'produceplanner/produceplan_form.html'
    
    def get_success_url(self):
        return reverse_lazy('produceplanner:overview_detail', kwargs={'pk': self.object.produce_plan_overview.id})
    
    def form_valid(self, form):
        instance = form.save()
        
        plant_name = instance.plant.name
        if instance.variety:
            plant_name = f"{instance.plant.name} ({instance.variety.variety_name})"
        
        messages.success(self.request, f'Updated {plant_name} in the produce plan')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['overview'] = self.object.produce_plan_overview
        context['available_plants'] = Plant.objects.all().order_by('name')
        context['available_varieties'] = Variety.objects.all().order_by('variety_name')
        context['page_app'] = 'produceplanner'
        context['page_name'] = 'produceplan'
        context['page_action'] = 'update'
        return context

class ProducePlanDeleteView(LoginRequiredMixin, DeleteView):
    model = ProducePlan
    template_name = 'produceplanner/produceplan_confirm_delete.html'
    context_object_name = 'produceplan'
    
    def get_success_url(self):
        return reverse_lazy('produceplanner:overview_detail', kwargs={'pk': self.object.produce_plan_overview.id})
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, 'Produce removed from plan')
        return redirect(success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'produceplanner'
        context['page_name'] = 'produceplan'
        context['page_action'] = 'delete'
        return context