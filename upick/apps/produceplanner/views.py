from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import Group
from datetime import timedelta, datetime
from .models import ProducePlanOverview, ProducePlan, Plant
from apps.plants.models import Plant, Variety
from apps.planning.models import GardenConfiguration, GardenPlan
from .forms import ProducePlanOverviewForm

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
    overview = get_object_or_404(ProducePlanOverview, id=overview_id, garden_plan__group__in=request.user.groups.all())
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
                    variety__isnull=True,  # Only include plans without a variety
                    start_date__lte=week['date'] + timedelta(days=6),
                    end_date__gte=week['date']
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
                        start_date__lte=week['date'] + timedelta(days=6),
                        end_date__gte=week['date']
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

class ProducePlanOverviewListView(LoginRequiredMixin, ListView):
    model = ProducePlanOverview
    template_name = 'produceplanner/overview_list.html'
    context_object_name = 'overviews'

    def get_queryset(self):
        return super().get_queryset().filter(garden_plan__group__in=self.request.user.groups.all())

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
        # Only show garden plans that don't already have a produce plan overview and belong to the user
        existing_plans = ProducePlanOverview.objects.values_list('garden_plan_id', flat=True)
        form.fields['garden_plan'].queryset = GardenPlan.objects.filter(group__in=self.request.user.groups.all()).exclude(id__in=existing_plans)
        return form

    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a produce plan overview.')
            return self.form_invalid(form)
        form.instance.group = group
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
        return super().get_queryset().filter(garden_plan__group__in=self.request.user.groups.all())

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
        return super().get_queryset().filter(garden_plan__group__in=self.request.user.groups.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['produce_plans'] = self.object.produce_plans.all().select_related('plant')
        context['available_plants'] = Plant.objects.exclude(
            id__in=self.object.produce_plans.values_list('plant_id', flat=True)
        )
        context['page_app'] = 'produceplanner'
        context['page_name'] = 'overview'
        context['page_action'] = 'detail'
        return context

@login_required
@require_POST
def add_produce(request, overview_id):
    overview = get_object_or_404(ProducePlanOverview, id=overview_id)
    try:
        plant = get_object_or_404(Plant, id=request.POST.get('plant'))
        start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').date()
        
        # Get variety if provided
        variety_id = request.POST.get('variety')
        variety = None
        if variety_id and variety_id != 'null' and variety_id != '':
            variety = get_object_or_404(Variety, id=variety_id)

        if start_date > end_date:
            raise ValueError('Start date must be before end date')

        if start_date < overview.overall_start_date or end_date > overview.overall_end_date:
            raise ValueError('Dates must be within the overall plan dates')

        ProducePlan.objects.create(
            plant=plant,
            variety=variety,
            produce_plan_overview=overview,
            start_date=start_date,
            end_date=end_date
        )

        plant_name = plant.name
        if variety:
            plant_name = f"{plant.name} ({variety.variety_name})"
        
        messages.success(request, f'Added {plant_name} to the produce plan')
    except Exception as e:
        messages.error(request, str(e))

    return redirect('produceplanner:overview_detail', pk=overview_id)

@login_required
@require_POST
def delete_produce(request, plan_id):
    plan = get_object_or_404(ProducePlan, id=plan_id)
    overview_id = plan.produce_plan_overview.id
    plan.delete()
    messages.success(request, 'Produce removed from plan')
    return JsonResponse({'status': 'success'})