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
from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib.auth.models import Group
from .models import PlantingSchedule, GardenBed
from plants.models import Plant, Variety
from planning.models import GardenPlan

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
            bed.current_plants = bed.plantingschedule_set.filter(
                status__in=['PLANNED', 'PLANTED']
            ).select_related('variety').order_by('variety__variety_name')

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
        # Set default year from query params or current year
        year = self.request.GET.get('year', datetime.now().year)
        try:
            year = int(year)
        except (TypeError, ValueError):
            year = datetime.now().year
        return {'year': year}

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
            .select_related('variety', 'garden_plan')\
            .order_by('-garden_plan__year', 'variety__variety_name')
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

@login_required
def schedule_list(request):
    """Display list of planting schedules grouped by garden bed."""
    # Get available years from garden plans
    garden_plans = GardenPlan.objects.filter(group__in=request.user.groups.all()).order_by('year')
    available_years = garden_plans.values_list('year', flat=True).distinct()
    
    # Get selected year (default to latest year)
    selected_year = request.GET.get('year')
    if not selected_year and available_years:
        selected_year = available_years[0]
    elif selected_year:
        selected_year = int(selected_year)
    
    # Get garden beds and schedules for selected year
    garden_beds = GardenBed.objects.filter(group__in=request.user.groups.all(), year=selected_year)
    schedules = PlantingSchedule.objects.filter(
        garden_bed__group__in=request.user.groups.all(),
        garden_plan__year=selected_year
    ) if selected_year else PlantingSchedule.objects.none()
    
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
        'available_years': available_years,
        'selected_year': selected_year,
    }
    return render(request, 'schedule/schedule_list.html', context)

@login_required
def schedule_detail(request, schedule_id):
    """Display details of a specific planting schedule."""
    schedule = get_object_or_404(PlantingSchedule, id=schedule_id, garden_bed__group__in=request.user.groups.all())
    
    context = {
        'schedule': schedule,
        'status_choices': PlantingSchedule._meta.get_field('status').choices,
    }
    return render(request, 'schedule/schedule_detail.html', context)

@login_required
def schedule_create(request):
    """Create a new planting schedule."""
    if request.method == 'POST':
        garden_bed_id = request.POST.get('garden_bed')
        variety_id = request.POST.get('variety')
        quantity = request.POST.get('quantity')
        rows = request.POST.get('rows')
        
        try:
            garden_bed = get_object_or_404(GardenBed, id=garden_bed_id, group__in=request.user.groups.all())
            variety = get_object_or_404(Variety, id=variety_id, variety_plant__group__in=request.user.groups.all())
            
            garden_plan_id = request.POST.get('garden_plan')
            garden_plan = None
            if garden_plan_id:
                garden_plan = get_object_or_404(GardenPlan, id=garden_plan_id, group__in=request.user.groups.all())

            # Handle dates
            inside_date = request.POST.get('inside_planting_date')
            outside_date = request.POST.get('outside_planting_date')
            harvest_date = request.POST.get('harvest_date')

            schedule = PlantingSchedule.objects.create(
                garden_bed=garden_bed,
                variety=variety,
                garden_plan=garden_plan,
                quantity=quantity,
                rows=rows,
                inside_planting_date=datetime.strptime(inside_date, '%Y-%m-%d').date() if inside_date else None,
                outside_planting_date=datetime.strptime(outside_date, '%Y-%m-%d').date() if outside_date else None,
                harvest_date=datetime.strptime(harvest_date, '%Y-%m-%d').date() if harvest_date else None,
                group=get_user_group(request)
            )
            
            messages.success(request, 'Planting schedule created successfully.')
            return redirect('schedule:detail', schedule_id=schedule.id)
            
        except Exception as e:
            messages.error(request, f'Error creating schedule: {str(e)}')
            # Get selected_year from POST data if it exists
            selected_year = request.POST.get('selected_year')
            if selected_year:
                return redirect(f'schedule:list?year={selected_year}')
            return redirect('schedule:list')
    
    # Get selected year from query parameters (passed from the schedule list page)
    selected_year = request.GET.get('year')
    if selected_year:
        try:
            selected_year = int(selected_year)
        except (ValueError, TypeError):
            # If year is invalid, use current year as default
            selected_year = datetime.now().year
    else:
        # If no year provided, use current year as default
        selected_year = datetime.now().year

    # Filter garden beds by the selected year
    garden_beds = GardenBed.objects.filter(group__in=request.user.groups.all(), year=selected_year)
    varieties = Variety.objects.filter(
        Q(variety_plant__group__in=request.user.groups.all()) | Q(variety_plant__group=None)
        ).select_related('variety_plant')
    garden_plans = GardenPlan.objects.filter(group__in=request.user.groups.all(), year=selected_year).order_by('-year', 'name')
    
    # Prepare JSON data for JavaScript
    garden_plans_json = [{'id': plan.id, 'year': plan.year, 'name': plan.name} for plan in garden_plans]
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
        variety_data = {
            'days_to_maturity': variety.variety_days_to_maturity,
            'days_from_seed_to_transplant': variety.variety_days_from_seed_to_transplant,
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

    context = {
        'garden_beds': garden_beds,
        'varieties': varieties,
        'garden_plans': garden_plans,
        'garden_plans_json': garden_plans_json,
        'varieties_json': varieties_json,
        'varieties_data': varieties_data,
        'page_app': 'schedule',
        'page_name': 'schedule',
        'page_action': 'form',
        'groups': Group.objects.all(),
        'selected_year': selected_year  # Add selected year to context
    }
    return render(request, 'schedule/schedule_form.html', context)

@login_required
def schedule_duplicate(request, schedule_id):
    """Duplicate an existing planting schedule."""
    original_schedule = get_object_or_404(PlantingSchedule, id=schedule_id, garden_bed__group__in=request.user.groups.all())
    
    # Create a new schedule with the same attributes as the original
    new_schedule = PlantingSchedule.objects.create(
        garden_bed=original_schedule.garden_bed,
        variety=original_schedule.variety,
        garden_plan=original_schedule.garden_plan,
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

@login_required
def schedule_edit(request, schedule_id):
    """Edit an existing planting schedule."""
    schedule = get_object_or_404(PlantingSchedule, id=schedule_id, garden_bed__group__in=request.user.groups.all())
    
    if request.method == 'POST':
        try:
            # Handle garden bed change
            garden_bed_id = request.POST.get('garden_bed')
            if garden_bed_id:
                garden_bed = get_object_or_404(GardenBed, id=garden_bed_id, group__in=request.user.groups.all())
                schedule.garden_bed = garden_bed

            # Handle garden plan change
            garden_plan_id = request.POST.get('garden_plan')
            if garden_plan_id:
                garden_plan = get_object_or_404(GardenPlan, id=garden_plan_id, group__in=request.user.groups.all())
                schedule.garden_plan = garden_plan
                
            # Handle variety change
            variety_id = request.POST.get('variety')
            if variety_id:
                variety = get_object_or_404(Variety, id=variety_id)
                schedule.variety = variety

            schedule.quantity = request.POST.get('quantity')
            schedule.rows = request.POST.get('rows')
            schedule.notes = request.POST.get('notes')
            schedule.location_notes = request.POST.get('location_notes')
            schedule.status = request.POST.get('status')
            
            # Handle dates
            inside_date = request.POST.get('inside_planting_date')
            outside_date = request.POST.get('outside_planting_date')
            harvest_date = request.POST.get('harvest_date')
            
            if inside_date:
                schedule.inside_planting_date = datetime.strptime(inside_date, '%Y-%m-%d').date()
            if outside_date:
                schedule.outside_planting_date = datetime.strptime(outside_date, '%Y-%m-%d').date()
            if harvest_date:
                schedule.harvest_date = datetime.strptime(harvest_date, '%Y-%m-%d').date()
            
            schedule.save()
            messages.success(request, 'Schedule updated successfully.')
            return redirect('schedule:detail', schedule_id=schedule.id)
            
        except Exception as e:
            messages.error(request, f'Error updating schedule: {str(e)}')
    
    # Get all garden beds for the user
    garden_beds = GardenBed.objects.filter(group__in=request.user.groups.all())
    
    # Get all garden plans for the user
    garden_plans = GardenPlan.objects.filter(group__in=request.user.groups.all()).order_by('year')
    
    # Get all varieties for the user's groups or with no group
    varieties = Variety.objects.filter(
        Q(variety_plant__group__in=request.user.groups.all()) | Q(variety_plant__group=None)
    ).select_related('variety_plant').order_by('variety_plant__name', 'id')
    
    # Prepare JSON data for JavaScript
    garden_plans_json = [{'id': plan.id, 'year': plan.year, 'name': plan.name} for plan in garden_plans]
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
        variety_data = {
            'days_to_maturity': variety.variety_days_to_maturity,
            'days_from_seed_to_transplant': variety.variety_days_from_seed_to_transplant,
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

    context = {
        'schedule': schedule,
        'garden_beds': garden_beds,
        'garden_plans': garden_plans,
        'varieties': varieties,
        'garden_plans_json': garden_plans_json,
        'varieties_json': varieties_json,
        'status_choices': PlantingSchedule._meta.get_field('status').choices,
        'varieties_data': varieties_data,
    }
    return render(request, 'schedule/schedule_form.html', context)

@require_POST
def update_planting_date(request, schedule_id):
    """Update the outside planting date and harvest date for a planting schedule."""
    try:
        schedule = get_object_or_404(PlantingSchedule, id=schedule_id)
        date_str = request.POST.get('planting_date')
        planting_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
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
    
    try:
        # Handle ISO format dates from FullCalendar (e.g. 2025-01-26T00:00:00-06:00)
        start_date = datetime.fromisoformat(start).date()
        end_date = datetime.fromisoformat(end).date()
    except (ValueError, TypeError):
        return JsonResponse({'error': f'Invalid date format. Got start={start}, end={end}'}, status=400)
    
    schedules = PlantingSchedule.objects.filter(garden_bed__group__in=request.user.groups.all())
    
    # Apply filters
    if status_filter and status_filter[0]:
        schedules = schedules.filter(status__in=status_filter)
    if beds_filter and beds_filter[0]:
        schedules = schedules.filter(garden_bed_id__in=beds_filter)
    
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
    
    return JsonResponse(events, safe=False)


@login_required
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
