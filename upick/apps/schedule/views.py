from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from calendar import monthcalendar, month_name
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta, date
from django.db.models import Q
from django.contrib.auth.models import Group
from .models import PlantingSchedule, GardenBed, TodoTask, TodoList
from .forms import TodoTaskForm, TodoListForm
from apps.plants.models import Plant, Variety
from .forms import PlantingScheduleForm
from apps.produceplanner.models import ProducePlan, ProducePlanOverview
from apps.planning.models import GardenConfiguration
import json

# Custom JSON encoder to handle date objects
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime('%m/%d/%Y')  # Format as mm/dd/yyyy
        return super().default(obj)

# Helper function to ensure JSON is properly serialized
def safe_json_dumps(data):
    """Safely convert data to JSON string with proper date formatting"""
    try:
        return json.dumps(data, cls=DateEncoder, ensure_ascii=False)
    except Exception as e:
        print(f"Error serializing to JSON: {e}")
        # Return an empty object as fallback
        return '{}'

def get_user_group(request):
    """Get the user's active group or return None if user has no groups.
    Also adds an error message if the user has no groups.
    """
    if not request.user.groups.exists():
        messages.error(request, 'You must be a member of at least one group to perform this action. Please contact your administrator.')
        return None
    return request.user.groups.first()


# Garden Bed Views
class GardenBedListView(LoginRequiredMixin, ListView):
    model = GardenBed
    template_name = 'schedule/garden_bed_list.html'
    context_object_name = 'garden_beds'

    def get_queryset(self):
        queryset = GardenBed.objects.filter(group__in=self.request.user.groups.all())\
            .prefetch_related('plantingschedule_set__variety')

        # Filter by year if provided
        year = self.request.GET.get('year')
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(year=year)
            except (TypeError, ValueError):
                pass
        
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        garden_beds = context['garden_beds']
        
        # For each garden bed, get its current plants
        for bed in garden_beds:
            bed.current_plants = bed.plantingschedule_set.all().select_related('variety').order_by('variety__variety_name')

        # Get current year and available years
        current_year = datetime.now().year
        available_years = list(GardenBed.objects.filter(group__in=self.request.user.groups.all())\
            .exclude(year__isnull=True)\
            .values_list('year', flat=True)\
            .distinct()\
            .order_by('-year'))

        # Add current year to available years if not present
        if current_year not in available_years:
            available_years.append(current_year)
            available_years.sort(reverse=True)

        # Get selected year from query params
        selected_year = self.request.GET.get('year')
        if selected_year:
            try:
                selected_year = int(selected_year)
            except (TypeError, ValueError):
                selected_year = None

        context.update({
            'page_app': 'schedule',
            'page_name': 'garden_bed',
            'page_action': 'list',
            'current_year': current_year,
            'available_years': available_years,
            'selected_year': selected_year,
        })
        return context

class GardenBedCreateView(LoginRequiredMixin, CreateView):
    model = GardenBed
    template_name = 'schedule/garden_bed_form.html'
    fields = ['name', 'year', 'width_feet', 'length_feet', 'description']
    def get_success_url(self):
        # Maintain year filter when redirecting
        year = self.request.GET.get('year')
        base_url = reverse_lazy('schedule:garden_bed_list')
        if year:
            return f"{base_url}?year={year}"
        return base_url

    def get_initial(self):
        # Get garden configuration
        garden_config = GardenConfiguration.get_settings()
        # Set default year from query params or current year
        year = self.request.GET.get('year', datetime.now().year)
        try:
            year = int(year)
        except (TypeError, ValueError):
            year = datetime.now().year
        return {'year': year, 'width_feet': garden_config.default_bed_width, 'length_feet': garden_config.default_bed_length}

    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a garden bed.')
            return self.form_invalid(form)
        form.instance.group = group
        messages.success(self.request, 'Garden bed created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'schedule'
        context['page_name'] = 'garden_bed'
        context['page_action'] = 'form'
        context['groups'] = Group.objects.all()
        return context
        
    def form_invalid(self, form):
        messages.error(self.request, f'Error creating garden bed: {form.errors}')
        return super().form_invalid(form)

class GardenBedUpdateView(LoginRequiredMixin, UpdateView):
    model = GardenBed
    template_name = 'schedule/garden_bed_form.html'
    fields = ['name', 'year', 'width_feet', 'length_feet', 'description']
    context_object_name = 'garden_bed'
    def get_success_url(self):
        # Maintain year filter when redirecting
        year = self.request.GET.get('year')
        base_url = reverse_lazy('schedule:garden_bed_list')
        if year:
            return f"{base_url}?year={year}"
        return base_url

    def get_queryset(self):
        return GardenBed.objects.filter(group__in=self.request.user.groups.all())

    def form_valid(self, form):
        messages.success(self.request, 'Garden bed updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'schedule'
        context['page_name'] = 'garden_bed'
        context['page_action'] = 'form'
        return context

class GardenBedDetailView(LoginRequiredMixin, DetailView):
    model = GardenBed
    template_name = 'schedule/garden_bed_detail.html'
    context_object_name = 'garden_bed'

    def get_queryset(self):
        return GardenBed.objects.filter(group__in=self.request.user.groups.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        garden_bed = self.get_object()
        context['page_app'] = 'schedule'
        context['page_name'] = 'garden_bed'
        context['page_action'] = 'detail'
        context['planting_schedules'] = garden_bed.plantingschedule_set.all()\
            .select_related('variety', 'produce_plan')\
            .order_by('-produce_plan__year', 'variety__variety_name')
        return context


class GardenBedDeleteView(LoginRequiredMixin, DeleteView):
    model = GardenBed
    def get_success_url(self):
        # Maintain year filter when redirecting
        year = self.request.GET.get('year')
        base_url = reverse_lazy('schedule:garden_bed_list')
        if year:
            return f"{base_url}?year={year}"
        return base_url

    def get_queryset(self):
        return GardenBed.objects.filter(group__in=self.request.user.groups.all())

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Garden bed deleted successfully.')
        return super().delete(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Redirect GET requests to the list view
        return redirect('schedule:garden_bed_list')

class ViewPlantingScheduleView(LoginRequiredMixin, DetailView):
    model = ProducePlanOverview
    template_name = 'schedule/view_planning_schedule.html'
    context_object_name = 'schedule'

    def get_queryset(self):
        return ProducePlanOverview.objects.filter(group__in=self.request.user.groups.all(),
                                                id=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        produceplan = ProducePlanOverview.objects.filter(id=self.kwargs['pk']).first()
        # Get garden beds and schedules for selected year
        schedules_list = PlantingSchedule.objects.filter(produce_plan=produceplan)
        garden_beds = GardenBed.objects.filter(group__in=self.request.user.groups.all())

        # Group schedules by garden bed
        schedule_by_bed = {}
        for bed in garden_beds:
            schedule_by_bed[bed] = schedules_list.filter(garden_bed=bed)
    
        context = {
            'schedule_by_bed': schedule_by_bed,
            'produceplan': produceplan,
            'page_app': 'schedule',
            'page_name': 'schedule',
            'page_action': 'list',
        }
        return context

@login_required
def schedule_list(request):
    """Display list of planting schedules grouped by garden bed."""
    # Get available years from garden plans
    produce_plans = ProducePlanOverview.objects.filter(group__in=request.user.groups.all()).order_by('year')
    #bgl
    # Get garden beds and schedules for selected year
    garden_beds = GardenBed.objects.filter(group__in=request.user.groups.all())
    schedules = PlantingSchedule.objects.filter(
        garden_bed__group__in=request.user.groups.all(),
        produce_plan__in=produce_plans
    )
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        schedules = schedules.filter(status=status)
    
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            schedules = schedules.filter(
                Q(inside_planting_date__range=(start, end)) |
                Q(outside_planting_date__range=(start, end)) |
                Q(harvest_date__range=(start, end))
            )
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
    
    # Group schedules by garden bed
    schedule_by_bed = {}
    for bed in garden_beds:
        schedule_by_bed[bed] = schedules.filter(garden_bed=bed)
    
    context = {
        'schedule_by_bed': schedule_by_bed,
        'status_choices': PlantingSchedule._meta.get_field('status').choices,
        'selected_status': status,
        'page_app': 'schedule',
        'page_name': 'schedule',
        'page_action': 'list',
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'schedule/schedule_list.html', context)

class ScheduleDetailView(LoginRequiredMixin, DetailView):
    """Class-based view for displaying details of a specific planting schedule."""
    model = PlantingSchedule
    template_name = 'schedule/schedule_detail.html'
    context_object_name = 'schedule'
    pk_url_kwarg = 'schedule_id'
    
    def get_queryset(self):
        return PlantingSchedule.objects.filter(garden_bed__group__in=self.request.user.groups.all())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = PlantingSchedule._meta.get_field('status').choices
        
        # Get the next schedule ID for navigation
        current_schedule = self.get_object()
        user_groups = self.request.user.groups.all()
        
        # Get the next schedule (by ID)
        next_schedule = PlantingSchedule.objects.filter(
            garden_bed__group__in=user_groups,
            id__gt=current_schedule.id
        ).order_by('id').first()
        
        # If no next schedule exists, get the first one (circular navigation)
        if not next_schedule:
            next_schedule = PlantingSchedule.objects.filter(
                garden_bed__group__in=user_groups
            ).order_by('id').first()
        
        context['next_schedule'] = next_schedule
        return context

class ScheduleCreateView(LoginRequiredMixin, CreateView):
    """Class-based view for creating a new planting schedule."""
    model = PlantingSchedule
    form_class = PlantingScheduleForm
    template_name = 'schedule/schedule_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass request to the form for filtering querysets
        kwargs['request'] = self.request
        
        # Get selected year from query parameters or use current year
        produceplanid = self.request.GET.get('produceplanid')
        if produceplanid:
            kwargs['produceplanid'] = produceplanid
        return kwargs
    
    def get_success_url(self):
        if self.request.GET.get('produceplanid'):
            return reverse_lazy('schedule:view_planning_schedule', kwargs={'pk': self.request.GET.get('produceplanid')})
        return reverse_lazy('schedule:detail', kwargs={'schedule_id': self.object.id})
    
    def form_valid(self, form):
        # Set the group for the planting schedule
        form.instance.group = get_user_group(self.request)
        if not form.instance.group:
            form.add_error(None, 'You must be a member of at least one group to create a planting schedule.')
            return self.form_invalid(form)
        
        instance = form.save(commit=False)
        instance.group = get_user_group(self.request)
        instance.schedule_status = self.request.POST.get('status')
        instance.schedule_notes = self.request.POST.get('notes')
        instance.schedule_location_notes = self.request.POST.get('location_notes')
        harvest_date_str = self.request.POST.get('harvest_date')
        if harvest_date_str:
            harvest_date = datetime.strptime(harvest_date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
            instance.expected_harvest_date = harvest_date
        inside_planting_date_str = self.request.POST.get('inside_planting_date')
        if inside_planting_date_str:
            inside_planting_date = datetime.strptime(inside_planting_date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
            instance.inside_planting_date = inside_planting_date
        outside_planting_date_str = self.request.POST.get('outside_planting_date')
        if outside_planting_date_str:
            outside_planting_date = datetime.strptime(outside_planting_date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
            instance.outside_planting_date = outside_planting_date
        variety = Variety.objects.get(id=self.request.POST.get('variety'))
        instance.variety = variety
        garden_bed = GardenBed.objects.get(id=self.request.POST.get('garden_bed'))
        instance.garden_bed = garden_bed
        produce_planObj = ProducePlanOverview.objects.get(id=self.request.POST.get('produce_plan'))
        instance.produce_plan = produce_planObj
        instance.save() 

        messages.success(self.request, 'Planting schedule created successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Don't add error message here as we're displaying errors in the template
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all garden beds for the user
        garden_beds = GardenBed.objects.filter(group__in=self.request.user.groups.all())
        
        # Get garden configuration
        garden_config = GardenConfiguration.get_settings()
                
        # Get varieties for JavaScript data
        varieties = Variety.objects.filter(
            Q(variety_plant__group__in=self.request.user.groups.all()) | Q(variety_plant__group=None)
        ).select_related('variety_plant').order_by('variety_plant__name', 'id')
        
        # Get produce plans for JavaScript data
        produce_plans = ProducePlanOverview.objects.filter(
            group__in=self.request.user.groups.all()
        ).order_by('-year', 'name')

        selectedproduce_plan = ProducePlanOverview.objects.filter(id=self.request.GET.get('produceplanid')).first()
        
        # Prepare JSON data for JavaScript
        produce_plans_json = [{'id': plan.id, 'year': plan.year, 'name': plan.name} for plan in produce_plans]
        varieties_json = [
            {
                'id': variety.id, 
                'name': variety.variety_plant.name if variety.variety_plant else '', 
                'variety_name': variety.variety_name
            } 
            for variety in varieties
        ]
        
        # Get variety data for date calculations
        varieties_data = {}
        for variety in varieties:
            if variety.variety_days_from_frost_to_transplant is None:
                earlies_outside_planting_date = garden_config.spring_frost_date
            else:
                earlies_outside_planting_date = garden_config.spring_frost_date + timedelta(days=variety.variety_days_from_frost_to_transplant)
            
            variety_data = {
                'earliest_outside_planting_date': earlies_outside_planting_date,
                'spring_frost_date': garden_config.spring_frost_date,
                'fall_frost_date': garden_config.fall_frost_date,
                'days_to_germinate': variety.variety_plant.days_to_germinate,
                'days_to_maturity': variety.variety_days_to_maturity,
                'days_from_seed_to_transplant': variety.variety_days_from_seed_to_transplant,
                'days_from_frost_to_transplant': variety.variety_days_from_frost_to_transplant,
                'planting_method': variety.variety_planting_method,
            }
            
            # If variety doesn't have values, use the plant's values
            if variety.variety_plant:
                if not variety_data['days_to_maturity'] and variety.variety_plant.days_to_maturity:
                    variety_data['days_to_maturity'] = variety.variety_plant.days_to_maturity
                    
                if not variety_data['days_from_seed_to_transplant'] and variety.variety_plant.days_from_seed_to_transplant:
                    variety_data['days_from_seed_to_transplant'] = variety.variety_plant.days_from_seed_to_transplant
                    
                if not variety_data['planting_method']:
                    variety_data['planting_method'] = variety.variety_plant.planting_method
                    
            varieties_data[variety.id] = variety_data

        # Convert varieties_data to JSON for JavaScript using the custom encoder and helper function
        varieties_data_json = safe_json_dumps(varieties_data)
        
        context.update({
            'selectedproduce_plan': selectedproduce_plan,
            'spring_frost_date': garden_config.spring_frost_date,
            'fall_frost_date': garden_config.fall_frost_date,
            'garden_beds': garden_beds,
            'varieties': varieties,
            'produce_plans': produce_plans,
            'produce_plans_json': produce_plans_json,
            'varieties_json': varieties_json,
            'varieties_data_json': varieties_data_json,
            'varieties_data': varieties_data,
            'page_app': 'schedule',
            'page_name': 'schedule',
            'page_action': 'form',
        })
        return context

@login_required
def schedule_duplicate(request, schedule_id):
    """Duplicate an existing planting schedule."""
    original_schedule = get_object_or_404(PlantingSchedule, id=schedule_id, garden_bed__group__in=request.user.groups.all())
    
    # Create a new schedule with the same attributes as the original
    new_schedule = PlantingSchedule.objects.create(
        garden_bed=original_schedule.garden_bed,
        variety=original_schedule.variety,
        produce_plan=original_schedule.produce_plan,
        group=original_schedule.group,
        seed_inventory=original_schedule.seed_inventory,
        inside_planting_date=original_schedule.inside_planting_date,
        outside_planting_date=original_schedule.outside_planting_date,
        harvest_date=original_schedule.harvest_date,
        quantity=original_schedule.quantity,
        rows=original_schedule.rows,
        notes=original_schedule.notes,
        location_notes=original_schedule.location_notes,
        status='PLANNED',  # Always set status to PLANNED for the duplicate
        succession_group=original_schedule.succession_group,
        x_position=original_schedule.x_position,
        y_position=original_schedule.y_position
    )
    
    messages.success(request, f'Successfully duplicated planting schedule for {original_schedule.variety.variety_name}')
    return redirect('schedule:edit', schedule_id=new_schedule.id)

class ScheduleUpdateView(LoginRequiredMixin, UpdateView):
    """Class-based view for editing an existing planting schedule."""
    model = PlantingSchedule
    form_class = PlantingScheduleForm
    template_name = 'schedule/schedule_form.html'
    context_object_name = 'schedule'
    pk_url_kwarg = 'schedule_id'
    
    def get_queryset(self):
        """Ensure user can only edit schedules from their groups."""
        return PlantingSchedule.objects.filter(garden_bed__group__in=self.request.user.groups.all())
    
    def get_form_kwargs(self):
        """Pass request to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        
        # Get the year from the produce plan or current year
        schedule = self.get_object()
        if schedule.produce_plan:
            selected_year = schedule.produce_plan.year
        elif schedule.garden_bed and schedule.garden_bed.year:
            selected_year = schedule.garden_bed.year
        else:
            selected_year = datetime.now().year
            
        kwargs['selected_year'] = selected_year
        return kwargs
    
    def get_success_url(self):
        """Redirect to the schedule detail page."""
        return reverse_lazy('schedule:detail', kwargs={'schedule_id': self.object.id})
    
    def form_valid(self, form):
        """Process the form data and save the schedule."""
        try:
            instance = form.save(commit=False)
            instance.group = get_user_group(self.request)
            instance.schedule_status = self.request.POST.get('status')
            instance.schedule_notes = self.request.POST.get('notes')
            instance.schedule_location_notes = self.request.POST.get('location_notes')
            produceplan = ProducePlanOverview.objects.get(id=self.request.POST.get('produce_plan'))
            instance.produce_plan = produceplan
            harvest_date_str = self.request.POST.get('harvest_date')
            if harvest_date_str:
                harvest_date = datetime.strptime(harvest_date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
                instance.expected_harvest_date = harvest_date
            inside_planting_date_str = self.request.POST.get('inside_planting_date')
            if inside_planting_date_str:
                inside_planting_date = datetime.strptime(inside_planting_date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
                instance.inside_planting_date = inside_planting_date
            outside_planting_date_str = self.request.POST.get('outside_planting_date')
            if outside_planting_date_str:
                outside_planting_date = datetime.strptime(outside_planting_date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
                instance.outside_planting_date = outside_planting_date
            variety = Variety.objects.get(id=self.request.POST.get('variety'))
            instance.variety = variety
            garden_bed = GardenBed.objects.get(id=self.request.POST.get('garden_bed'))
            instance.garden_bed = garden_bed
            instance.save()

            messages.success(self.request, 'Schedule updated successfully.')
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Error updating schedule: {str(e)}')
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add additional context data for the template."""
        context = super().get_context_data(**kwargs)
        
        # Get all garden beds for the user
        garden_beds = GardenBed.objects.filter(group__in=self.request.user.groups.all())
        
        # Get all produce plans for the user
        produce_plans = ProducePlanOverview.objects.filter(group__in=self.request.user.groups.all()).order_by('year')

        garden_config = GardenConfiguration.get_settings()
        
        # Get all varieties for the user's groups or with no group
        varieties = Variety.objects.filter(
            Q(variety_plant__group__in=self.request.user.groups.all()) | Q(variety_plant__group=None)
        ).select_related('variety_plant').order_by('variety_plant__name', 'id')
        
        # Prepare JSON data for JavaScript
        produce_plans_json = json.dumps([
            {
                'id': plan.id,
                'year': plan.year,
                'name': plan.name
            } 
            for plan in produce_plans
        ], ensure_ascii=False)

        varieties_json = json.dumps([
            {
                'id': variety.id, 
                'name': variety.variety_plant.name if variety.variety_plant else "", 
                'variety_name': variety.variety_name
            } 
            for variety in varieties
        ], ensure_ascii=False)
        
        # Get variety data for date calculations
        varieties_data = {}
        for variety in varieties:
            earlies_outside_planting_date = garden_config.spring_frost_date + timedelta(days=variety.variety_days_from_frost_to_transplant)
            variety_data = {
                'earliest_outside_planting_date': earlies_outside_planting_date,
                'spring_frost_date': garden_config.spring_frost_date,
                'fall_frost_date': garden_config.fall_frost_date,
                'days_to_germinate': variety.variety_plant.days_to_germinate if variety.variety_plant.days_to_germinate else 0,
                'days_to_maturity': variety.variety_days_to_maturity,
                'days_from_seed_to_transplant': variety.variety_days_from_seed_to_transplant,
                'days_from_frost_to_transplant': variety.variety_days_from_frost_to_transplant,
                'planting_method': variety.variety_planting_method,
            }
            
            # If variety doesn't have values, use the plant's values
            if variety.variety_plant:
                if not variety_data['days_to_maturity'] and variety.variety_plant.days_to_maturity:
                    variety_data['days_to_maturity'] = variety.variety_plant.days_to_maturity
                    
                if not variety_data['days_from_seed_to_transplant'] and variety.variety_plant.days_from_seed_to_transplant:
                    variety_data['days_from_seed_to_transplant'] = variety.variety_plant.days_from_seed_to_transplant
                    
                if not variety_data['planting_method']:
                    variety_data['planting_method'] = variety.variety_plant.planting_method
                    
            varieties_data[str(variety.id)] = variety_data  # Convert key to string for JSON compatibility
        
        # Convert varieties_data to JSON for JavaScript using the custom encoder and helper function
        varieties_data_json = safe_json_dumps(varieties_data)
        
        # Debug: Print the first few items of the varieties_data dictionary
        #print(f"Varieties data sample: {list(varieties_data.items())[:3]}")
        #print(f"Varieties data keys: {list(varieties_data.keys())[:10]}")  
        #print(f"JSON type: {type(varieties_data_json)}")
        #print(f"JSON sample: {varieties_data_json[:100]}...")
        
        context.update({
            'garden_beds': garden_beds,
            'produce_plans': produce_plans,
            'varieties': varieties,
            'produce_plans_json': produce_plans_json,
            'varieties_json': varieties_json,
            'varieties_data_json': varieties_data_json,
            'status_choices': PlantingSchedule._meta.get_field('status').choices,
            'varieties_data': varieties_data,  # Keep the original for Python template usage if needed
            'page_app': 'schedule',
            'page_name': 'schedule',
            'page_action': 'edit',
        })
        return context

@require_POST
def update_planting_date(request, schedule_id):
    """Update the outside planting date and harvest date for a planting schedule."""
    try:
        schedule = get_object_or_404(PlantingSchedule, id=schedule_id)
        date_str = request.POST.get('planting_date')
        
        # Try to parse the date in mm/dd/yyyy format first
        try:
            planting_date = datetime.strptime(date_str, '%m/%d/%Y').date()
        except ValueError:
            # Fallback to YYYY-MM-DD format
            try:
                planting_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Please use MM/DD/YYYY format.'}, status=400)
        
        # Update the schedule's outside planting date
        schedule.outside_planting_date = planting_date
        
        # If it's a transplant, calculate the inside planting date
        if schedule.variety.variety_planting_method == 'TRANSPLANT' and schedule.variety.variety_days_from_seed_to_transplant:
            inside_date = planting_date - timedelta(days=schedule.variety.variety_days_from_seed_to_transplant)
            schedule.inside_planting_date = inside_date
        
        # Calculate and set harvest date if days_to_maturity is available
        if schedule.variety.variety_days_to_maturity:
            harvest_date = planting_date + timedelta(days=schedule.variety.variety_days_to_maturity)
            schedule.harvest_date = harvest_date
        
        schedule.save()
        
        message = f'Updated planting date to {planting_date}'
        if schedule.variety.variety_planting_method == 'TRANSPLANT' and schedule.variety.variety_days_from_seed_to_transplant:
            message += f', inside planting date to {schedule.inside_planting_date}'
        if schedule.variety.variety_days_to_maturity:
            message += f' and harvest date to {schedule.harvest_date}'
        
        return JsonResponse({
            'status': 'success',
            'message': message
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
def calendar_view(request):
    """Display the calendar view of planting schedules."""
    garden_beds = GardenBed.objects.filter(group__in=request.user.groups.all())
    context = {
        'garden_beds': garden_beds,
        'page_app': 'schedule',
        'page_name': 'schedule',
        'page_action': 'calendar'
    }
    return render(request, 'schedule/calendar.html', context)


@login_required
@require_GET
def get_calendar_events(request):
    """API endpoint to get calendar events based on filters."""
    start = request.GET.get('start')
    end = request.GET.get('end')
    status_filter = request.GET.get('status', '').split(',')
    beds_filter = request.GET.get('beds', '').split(',')
    types_filter = request.GET.get('types', '').split(',')
    todo_status_filter = request.GET.get('todo_status', '').split(',')
    
    try:
        # Handle ISO format dates from FullCalendar (e.g. 2025-01-26T00:00:00-06:00)
        start_date = datetime.fromisoformat(start).date()
        end_date = datetime.fromisoformat(end).date()
    except (ValueError, TypeError):
        return JsonResponse({'error': f'Invalid date format. Got start={start}, end={end}'}, status=400)
    
    schedules = PlantingSchedule.objects.filter(garden_bed__group__in=request.user.groups.all())
    todo_tasks = TodoTask.objects.filter(group__in=request.user.groups.all())
    
    # Apply filters
    if status_filter and status_filter[0]:
        schedules = schedules.filter(status__in=status_filter)
    if beds_filter and beds_filter[0]:
        schedules = schedules.filter(garden_bed_id__in=beds_filter)
    if todo_status_filter and todo_status_filter[0]:
        todo_tasks = todo_tasks.filter(status__in=todo_status_filter)
    
    events = []
    for schedule in schedules:
        if 'inside' in types_filter and schedule.inside_planting_date:
            if start_date <= schedule.inside_planting_date <= end_date:
                events.append({
                    'id': schedule.id,
                    'title': f'{schedule.variety.variety_name} - Inside Planting',
                    'start': schedule.inside_planting_date.isoformat(),
                    'description': f'Garden Bed: {schedule.garden_bed.name}',
                    'className': 'inside-planting',
                })
        
        if 'outside' in types_filter and schedule.outside_planting_date:
            if start_date <= schedule.outside_planting_date <= end_date:
                events.append({
                    'id': schedule.id,
                    'title': f'{schedule.variety.variety_name} - Outside Planting',
                    'start': schedule.outside_planting_date.isoformat(),
                    'description': f'Garden Bed: {schedule.garden_bed.name}',
                    'className': 'outside-planting',
                })
        
        if 'harvest' in types_filter and schedule.harvest_date:
            if start_date <= schedule.harvest_date <= end_date:
                events.append({
                    'id': schedule.id,
                    'title': f'{schedule.variety.variety_name} - Harvest',
                    'start': schedule.harvest_date.isoformat(),
                    'description': f'Garden Bed: {schedule.garden_bed.name}',
                    'className': 'harvest',
                })
    
    for todo_task in todo_tasks:
        if start_date <= todo_task.due_date <= end_date:
            events.append({
                'id': todo_task.id,
                'title': todo_task.title,
                'start': todo_task.due_date.isoformat(),
                'description': f'TODO: {todo_task.title}',
                'className': 'todo',
            })
    
    return JsonResponse(events, safe=False)


# TodoTask Views
class TodoTaskListView(LoginRequiredMixin, ListView):
    model = TodoTask
    template_name = 'schedule/todo_task_list.html'
    context_object_name = 'todo_tasks'
    
    def get_queryset(self):
        queryset = TodoTask.objects.filter(group__in=self.request.user.groups.all())
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by priority if provided
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by garden bed if provided
        garden_bed_id = self.request.GET.get('garden_bed')
        if garden_bed_id:
            try:
                garden_bed_id = int(garden_bed_id)
                queryset = queryset.filter(garden_bed_id=garden_bed_id)
            except (TypeError, ValueError):
                pass
        
        return queryset.order_by('due_date', 'priority')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_app': 'schedule',
            'page_name': 'todo_task',
            'page_action': 'list',
            'status_choices': dict(TodoTask.STATUS_CHOICES),
            'priority_choices': dict(TodoTask.PRIORITY_CHOICES),
            'garden_beds': GardenBed.objects.filter(group__in=self.request.user.groups.all()),
            'selected_status': self.request.GET.get('status'),
            'selected_priority': self.request.GET.get('priority'),
            'selected_garden_bed': self.request.GET.get('garden_bed'),
        })
        return context


class TodoTaskCreateView(LoginRequiredMixin, CreateView):
    model = TodoTask
    form_class = TodoTaskForm
    template_name = 'schedule/todo_task_form.html'
    
    def get_success_url(self):
        return reverse_lazy('schedule:todo_task_list')
    
    def form_valid(self, form):
        instance = form.save(commit=False)
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a task.')
            return self.form_invalid(form)
        instance.group = group
        instance.save()
        messages.success(self.request, 'Task created successfully.')
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter garden beds and planting schedules by user's groups
        form.fields['garden_bed'].queryset = GardenBed.objects.filter(
            group__in=self.request.user.groups.all()
        )
        form.fields['planting_schedule'].queryset = PlantingSchedule.objects.filter(
            group__in=self.request.user.groups.all()
        )
        # Filter task lists by TodoList
        if 'tasklist' in form.fields:
            form.fields['tasklist'].queryset = TodoList.objects.filter(
                group__in=self.request.user.groups.all()
            )
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_app': 'schedule',
            'page_name': 'todo_task',
            'page_action': 'form',
        })
        return context


class TodoTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = TodoTask
    form_class = TodoTaskForm
    template_name = 'schedule/todo_task_form.html'
    context_object_name = 'todo_task'
    
    def get_success_url(self):
        return reverse_lazy('schedule:todo_task_list')
    
    def get_queryset(self):
        return TodoTask.objects.filter(group__in=self.request.user.groups.all())
    
    def form_valid(self, form):
        instance = form.save(commit=False)
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to update a task.')
            return self.form_invalid(form)
        instance.group = group
        instance.save()
        messages.success(self.request, 'Task updated successfully.')
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter garden beds and planting schedules by user's groups
        form.fields['garden_bed'].queryset = GardenBed.objects.filter(
            group__in=self.request.user.groups.all()
        )
        form.fields['planting_schedule'].queryset = PlantingSchedule.objects.filter(
            group__in=self.request.user.groups.all()
        )
        form.fields['tasklist'].queryset = TodoList.objects.filter(
            group__in=self.request.user.groups.all()
        )
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_app': 'schedule',
            'page_name': 'todo_task',
            'page_action': 'form',
        })
        return context

@login_required
def TodoTaskMarkComplete(request, pk):
    todo_task = get_object_or_404(TodoTask, pk=pk)
    todo_task.status = 'COMPLETED'
    todo_task.save()
    messages.success(request, 'Task marked as complete.')
    return redirect('schedule:todo_task_list')

class TodoTaskDetailView(LoginRequiredMixin, DetailView):
    model = TodoTask
    template_name = 'schedule/todo_task_detail.html'
    context_object_name = 'todo_task'
    
    def get_queryset(self):
        return TodoTask.objects.filter(group__in=self.request.user.groups.all())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_app': 'schedule',
            'page_name': 'todo_task',
            'page_action': 'detail'
        })
        return context


class TodoTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = TodoTask
    template_name = 'schedule/todo_task_confirm_delete.html'
    context_object_name = 'todo_task'
    
    def get_success_url(self):
        return reverse_lazy('schedule:todo_task_list')
    
    def get_queryset(self):
        return TodoTask.objects.filter(group__in=self.request.user.groups.all())
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Task deleted successfully.')
        return super().delete(request, *args, **kwargs)


# TodoList Views
class TodoListListView(LoginRequiredMixin, ListView):
    model = TodoList
    template_name = 'schedule/todo_list_list.html'
    context_object_name = 'todo_lists'
    
    def get_queryset(self):
        return TodoList.objects.filter(group__in=self.request.user.groups.all())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todo_tasks = TodoTask.objects.filter(tasklist__in=self.get_queryset())
        context['todo_tasks'] = todo_tasks
        context.update({
            'page_app': 'schedule',
            'page_name': 'todo_list',
            'page_action': 'list',
        })
        return context


class TodoListCreateView(LoginRequiredMixin, CreateView):
    model = TodoList
    form_class = TodoListForm
    template_name = 'schedule/todo_list_form.html'
    
    def get_success_url(self):
        return reverse_lazy('schedule:todo_list_list')
    
    def form_valid(self, form):
        instance = form.save(commit=False)
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a list.')
            return self.form_invalid(form)
        instance.group = group
        instance.save()
        messages.success(self.request, 'Todo list created successfully.')
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get the list of todo tasks for this list
        todo_tasks = TodoTask.objects.filter(tasklist=self.get_object())
        context['todo_tasks'] = todo_tasks
        context.update({
            'page_app': 'schedule',
            'page_name': 'todo_list',
            'page_action': 'form',
        })
        return context


class TodoListUpdateView(LoginRequiredMixin, UpdateView):
    model = TodoList
    form_class = TodoListForm
    template_name = 'schedule/todo_list_form.html'
    context_object_name = 'todo_list'
    
    def get_success_url(self):
        return reverse_lazy('schedule:todo_list_list')
    
    def get_queryset(self):
        return TodoList.objects.filter(group__in=self.request.user.groups.all())
    
    def form_valid(self, form):
        messages.success(self.request, 'Todo list updated successfully.')
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get the list of todo tasks for this list
        todo_tasks = TodoTask.objects.filter(tasklist=self.get_object())
        context['todo_tasks'] = todo_tasks
        context.update({
            'page_app': 'schedule',
            'page_name': 'todo_list',
            'page_action': 'form',
        })
        return context


class TodoListDetailView(LoginRequiredMixin, DetailView):
    model = TodoList
    template_name = 'schedule/todo_list_detail.html'
    context_object_name = 'todo_list'
    
    def get_queryset(self):
        return TodoList.objects.filter(group__in=self.request.user.groups.all())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todo_list = self.get_object()
        todo_tasks = TodoTask.objects.filter(tasklist=todo_list)
        context['todo_tasks'] = todo_tasks
        context.update({
            'page_app': 'schedule',
            'page_name': 'todo_list',
            'page_action': 'detail'
        })
        return context


class TodoListDeleteView(LoginRequiredMixin, DeleteView):
    model = TodoList
    template_name = 'schedule/todo_list_confirm_delete.html'
    context_object_name = 'todo_list'
    
    def get_success_url(self):
        return reverse_lazy('schedule:todo_list_list')
    
    def get_queryset(self):
        return TodoList.objects.filter(group__in=self.request.user.groups.all())
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Todo list deleted successfully.')
        return super().delete(request, *args, **kwargs)


def export_calendar_pdf(request):
    """Export the planting schedule as a PDF calendar."""
    # Get the month and year from the request, default to current month
    try:
        month = int(request.GET.get('month', datetime.now().month))
        year = int(request.GET.get('year', datetime.now().year))
    except ValueError:
        return HttpResponse('Invalid month or year', status=400)
    
    # Create the response object with PDF mime type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="garden-calendar-{year}-{month:02d}.pdf"'
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Title style - smaller than default
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,  # Reduced from default
        spaceAfter=1
    )
    
    # Date header style - compact
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Heading2'],
        fontSize=8,  # Reduced from 14
        spaceBefore=8,  # Reduced from 20
        spaceAfter=4,  # Reduced from 10
        leading=12
    )
    
    # Event style - compact
    event_style = ParagraphStyle(
        'EventStyle',
        parent=styles['Normal'],
        fontSize=8,  # Reduced from 11
        leftIndent=20,  # Reduced from 30
        spaceBefore=1,  # Reduced from 3
        spaceAfter=1,  # Reduced from 3
        leading=10
    )
    
    # Get all schedules for the month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()
    
    schedules = PlantingSchedule.objects.filter(
        garden_bed__group__in=request.user.groups.all()
    ).filter(
        Q(inside_planting_date__range=(start_date, end_date)) |
        Q(outside_planting_date__range=(start_date, end_date)) |
        Q(harvest_date__range=(start_date, end_date))
    )
    
    # Group events by date
    events_by_date = defaultdict(list)
    for schedule in schedules:
        if schedule.inside_planting_date and start_date <= schedule.inside_planting_date < end_date:
            events_by_date[schedule.inside_planting_date].append(
                f'🌱 (Inside) - Qty: {schedule.quantity} :: {schedule.variety.variety_plant.name} - {schedule.variety.variety_name}'
            )
        if schedule.outside_planting_date and start_date <= schedule.outside_planting_date < end_date:
            events_by_date[schedule.outside_planting_date].append(
                f'🪴 (Outside) - Qty: {schedule.quantity} :: {schedule.variety.variety_plant.name} - {schedule.variety.variety_name} :: {schedule.garden_bed.name} '
            )
        if schedule.harvest_date and start_date <= schedule.harvest_date < end_date:
            events_by_date[schedule.harvest_date].append(
                f'🌾 (Harvest)  - Qty: {schedule.quantity} :: {schedule.variety.variety_plant.name} - {schedule.variety.variety_name} :: {schedule.garden_bed.name}'
            )
    
    todo_tasks = TodoTask.objects.filter(
        group__in=request.user.groups.all()
    ).filter(
        Q(due_date__range=(start_date, end_date))
    )
    
    # Group todo tasks by date
    todo_tasks_by_date = defaultdict(list)
    for todo_task in todo_tasks:
        if todo_task.due_date and start_date <= todo_task.due_date < end_date:
            todo_tasks_by_date[todo_task.due_date].append(
                f'TODO: {todo_task.title}'
            )
    
    # Create styles for the list format
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Heading2'],
        fontSize=10,
        spaceBefore=10,
        spaceAfter=1,
    )
    
    event_style = ParagraphStyle(
        'EventStyle',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=30,
        spaceBefore=2,
        spaceAfter=2,
    )
    
    # Create styles for creation date
    created_style = ParagraphStyle(
        'CreatedStyle',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,  # Center
        textColor=colors.gray
    )

    # Create the document elements
    current_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    elements = [
        Paragraph(f'Garden Planner - {month_name[month]} {year}', title_style),
        Paragraph(f'Created: {current_time}', created_style),
    ]
    
    # Sort dates and add events
    for date in sorted(events_by_date.keys()):
        # Add the date header
        date_str = date.strftime('%A, %B %d, %Y')
        elements.append(Paragraph(date_str, date_style))
        
        # Add each event under the date
        for event in events_by_date[date]:
            elements.append(Paragraph(event, event_style))

    for date in sorted(todo_tasks_by_date.keys()):
        # Add the date header
        date_str = date.strftime('%A, %B %d, %Y')
        elements.append(Paragraph(date_str, date_style))
        
        # Add each todo task under the date
        for todo_task in todo_tasks_by_date[date]:
            elements.append(Paragraph(todo_task, event_style))
    
    # If no events, add a message
    if not events_by_date:
        elements.append(
            Paragraph(
                'No gardening activities scheduled for this month.',
                styles['Normal']
            )
        )
    
    # Build the PDF
    doc.build(elements)
    
    return response

class ScheduleDeleteView(DeleteView):
    model = PlantingSchedule
    template_name = 'schedule/schedule_confirm_delete.html'
    success_url = reverse_lazy('schedule:list')
