from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange, Calendar, SUNDAY
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.template.defaulttags import register

from apps.planning.models import GardenConfiguration
from .models import GardenBed, PlantingSchedule
from apps.plants.models import Variety
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from datetime import date, datetime
from django.template.response import TemplateResponse
import calendar 

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@admin.register(GardenBed)
class GardenBedAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'bed_dimensions', 'created_at')
    list_filter = ('group', 'year')
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'group',
                'description'
            )
        }),
        ('Dimensions', {
            'fields': (
                ('width_feet', 'length_feet'),
            )
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'square_feet')
    
    def bed_dimensions(self, obj):
        return format_html(
            '{} × {} ft <br><small>({} sq ft)</small>',
            obj.width_feet,
            obj.length_feet,
            float(obj.width_feet) * float(obj.length_feet)
        )
    bed_dimensions.short_description = 'Dimensions'
    
    def square_feet(self, obj):
        if obj.width_feet and obj.length_feet:
            return f"{float(obj.width_feet) * float(obj.length_feet)} square feet"
        return "N/A"
    square_feet.short_description = 'Total Area'

    def duplicate_bed(self, request, queryset):
        for bed in queryset:
            # Create a copy of the bed
            bed.pk = None
            bed.name = f"{bed.name} (Copy)"
            bed.save()
            messages.success(request, f'Successfully duplicated "{bed.name}"')
    
    duplicate_bed.short_description = "Duplicate selected beds"
    
    actions = ['duplicate_bed']
    
    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }

@admin.register(PlantingSchedule)
class PlantingScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'garden_bed',
        'variety',
        'status',
        'planting_method_display',
        'inside_planting_date',
        'outside_planting_date_display',
        'calculate_frost_date',
        'status',
        'bed_length_display',
    )
    list_filter = (
        'status',
        'garden_bed',
        'inside_planting_date',
        'outside_planting_date',
        'harvest_date',
        'variety__variety_planting_method'
    )
    search_fields = (
        'variety__variety_name',
        'garden_bed__name',
        'notes',
        'location_notes'
    )
    
    def outside_planting_date_display(self, obj):
        if obj.outside_planting_date:
            return obj.outside_planting_date.strftime('%b %d, %Y')
        return '-'
    outside_planting_date_display.short_description = 'Outside Planting Date'
    
    def planting_method_display(self, obj):
        # First check if variety has planting method defined
        if obj.variety.variety_planting_method:
            method = obj.variety.variety_planting_method
        # If not, use the plant's planting method
        elif obj.variety.variety_plant and obj.variety.variety_plant.planting_method:
            method = obj.variety.variety_plant.planting_method
        else:
            method = 'DIRECT'  # Default
            
        if method == 'DIRECT':
            return format_html('<span class="direct-seed">Direct Seed</span>')
        else:
            return format_html('<span class="transplant">Transplant</span>')
    planting_method_display.short_description = 'Planting Method'
    
    def bed_length_display(self, obj):
        length = obj.calculate_bed_length()
        if length:
            return f"{length}'"
        return '-'
    bed_length_display.short_description = "Bed Length Needed"
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set the group when creating a new object
            if request.user.groups.exists():
                obj.group = request.user.groups.first()
        super().save_model(request, obj, form, change)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "garden_bed":
            if request.user.groups.exists():
                kwargs["queryset"] = GardenBed.objects.filter(group__in=request.user.groups.all())
        elif db_field.name == "variety":
            if request.user.groups.exists():
                kwargs["queryset"] = Variety.objects.filter(
                    Q(variety_plant__group__in=request.user.groups.all()) | 
                    Q(variety_plant__group=None)
                ).select_related('variety_plant')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def calculate_frost_date(self, obj):
        if not obj.outside_planting_date:
            return '-'
            
        # Get the garden configuration for the user's group
        garden_config = None
        if obj.group:
            try:
                garden_config = GardenConfiguration.objects.get(group=obj.group)
            except GardenConfiguration.DoesNotExist:
                pass
        
        if not garden_config or not garden_config.last_frost_date:
            return '-'
            
        # Calculate days from last frost date
        last_frost = garden_config.last_frost_date
        if obj.outside_planting_date.year != last_frost.year:
            # Adjust to the same year for comparison
            last_frost = last_frost.replace(year=obj.outside_planting_date.year)
            
        days_diff = (obj.outside_planting_date - last_frost).days
        
        if days_diff < 0:
            return format_html('<span class="frost-warning">{} days before frost</span>', abs(days_diff))
        else:
            return f"{days_diff} days after frost"
    calculate_frost_date.short_description = "From Frost Date"
    
    # Action to duplicate selected schedules
    def duplicate_and_edit_schedule(self, request, queryset):
        if queryset.count() > 5:
            self.message_user(request, "You can only duplicate up to 5 schedules at once.", level=messages.WARNING)
            return
            
        for schedule in queryset:
            new_schedule = PlantingSchedule.objects.create(
                garden_bed=schedule.garden_bed,
                variety=schedule.variety,
                group=schedule.group,
                seed_inventory=schedule.seed_inventory,
                inside_planting_date=schedule.inside_planting_date,
                outside_planting_date=schedule.outside_planting_date,
                harvest_date=schedule.harvest_date,
                quantity=schedule.quantity,
                rows=schedule.rows,
                notes=schedule.notes,
                location_notes=schedule.location_notes,
                status='PLANNED',  # Reset status to PLANNED
                succession_group=schedule.succession_group + 1  # Increment succession group
            )
            
        self.message_user(request, f"{queryset.count()} schedule(s) duplicated successfully.")
    duplicate_and_edit_schedule.short_description = "Duplicate and Edit selected schedules"
    
    actions = ['duplicate_and_edit_schedule']
    
    # JavaScript and CSS for the admin interface
    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/planting_schedule.js',
            'schedule/js/admin.js',
        )
        css = {
            'all': ('admin/css/planting_schedule.css',)
        }
    
    # Custom fieldsets for the admin form
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'garden_bed',
                'variety',
                'seed_inventory',
                'quantity',
                'rows',
                'succession_group'
            ),
            'description': 'Basic planting information. Bed length will be calculated based on quantity, rows, and plant spacing.'
        }),
        ('Dates', {
            'fields': (
                'harvest_date',
                'inside_planting_date',
                'outside_planting_date'
            ),
            'description': 'Enter a target harvest date to automatically calculate planting dates, or enter planting dates directly.'
        }),
        ('Status & Notes', {
            'fields': (
                'status',
                'notes',
                'location_notes'
            )
        }),
        ('Position', {
            'fields': (
                ('x_position', 'y_position'),
            ),
            'classes': ('collapse',)
        })
    )
    
    # Custom template for the change list view
    change_list_template = 'admin/schedule/plantingschedule/change_list.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('calendar/', self.admin_site.admin_view(self.calendar_view), name='schedule_plantingschedule_calendar'),
            path('calendar/pdf/', self.admin_site.admin_view(self.calendar_pdf_view), name='schedule_plantingschedule_calendar_pdf'),
            path('add/calculate-dates/', self.admin_site.admin_view(self.calculate_dates), name='schedule_plantingschedule_calculate_dates_add'),
            path('<path:object_id>/calculate-dates', self.admin_site.admin_view(self.calculate_dates), name='schedule_plantingschedule_calculate_dates_change'),
            path('calendar/quick-add/', self.admin_site.admin_view(self.quick_add_event), name='quick-add-event'),
            path('calendar/quick-edit/<int:pk>/', self.admin_site.admin_view(self.quick_edit_event), name='quick-edit-event'),
            path('calendar/move-event/<int:pk>/', self.admin_site.admin_view(self.move_event), name='move-event'),
            path('calendar/delete-event/<int:pk>/', self.admin_site.admin_view(self.delete_event), name='delete-event'),
        ]
        return custom_urls + urls

    def quick_add_event(self, request):
        if request.method == 'POST':
            try:
                date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
                variety_id = request.POST.get('variety')
                bed_id = request.POST.get('garden_bed')
                event_type = request.POST.get('event_type')  # 'planting' or 'harvest'
                status = request.POST.get('status', 'PLANNED')
                
                # Check if user has permission for this bed
                bed = get_object_or_404(GardenBed, pk=bed_id)
                if not request.user.is_superuser and bed.owner != request.user:
                    return JsonResponse({'status': 'error', 'message': 'Permission denied for this garden bed'})
                
                planting = PlantingSchedule(
                    garden_bed_id=bed_id,
                    variety_id=variety_id,
                    status=status
                )
                
                if event_type == 'planting':
                    planting.inside_planting_date = date
                    # Calculate expected harvest date based on days_to_maturity
                    variety = planting.variety
                    if variety.days_to_maturity:
                        planting.harvest_date = date + timedelta(days=variety.days_to_maturity)
                else:
                    planting.harvest_date = date
                    # Calculate backward for planting date
                    variety = planting.variety
                    if variety.days_to_maturity:
                        planting.inside_planting_date = date - timedelta(days=variety.days_to_maturity)
                
                # If status is PLANTED, set outside planting date
                if status == 'PLANTED':
                    planting.outside_planting_date = date
                
                planting.save()
                return JsonResponse({'status': 'success', 'message': 'Event added successfully'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    def quick_edit_event(self, request, pk):
        planting = get_object_or_404(PlantingSchedule, pk=pk)
        if request.method == 'POST':
            try:
                date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
                event_type = request.POST.get('event_type')
                
                if event_type == 'planting':
                    planting.inside_planting_date = date
                    if planting.variety.days_to_maturity:
                        planting.harvest_date = date + timedelta(days=planting.variety.days_to_maturity)
                else:
                    planting.harvest_date = date
                    if planting.variety.days_to_maturity:
                        planting.inside_planting_date = date - timedelta(days=planting.variety.days_to_maturity)
                
                planting.save()
                return JsonResponse({'status': 'success', 'message': 'Event updated successfully'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    def move_event(self, request, pk):
        planting = get_object_or_404(PlantingSchedule, pk=pk)
        if request.method == 'POST':
            try:
                new_date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
                event_type = request.POST.get('event_type')
                
                if event_type == 'planting':
                    days_diff = (new_date - planting.inside_planting_date).days
                    planting.inside_planting_date = new_date
                    if planting.harvest_date:
                        planting.harvest_date = planting.harvest_date + timedelta(days=days_diff)
                else:
                    days_diff = (new_date - planting.harvest_date).days
                    planting.harvest_date = new_date
                    if planting.inside_planting_date:
                        planting.inside_planting_date = planting.inside_planting_date + timedelta(days=days_diff)
                
                planting.save()
                return JsonResponse({'status': 'success', 'message': 'Event moved successfully'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    def delete_event(self, request, pk):
        if request.method == 'POST':
            try:
                planting = get_object_or_404(PlantingSchedule, pk=pk)
                if not request.user.is_superuser and planting.garden_bed.owner != request.user:
                    return JsonResponse({'status': 'error', 'message': 'Permission denied'})
                
                planting.delete()
                return JsonResponse({'status': 'success', 'message': 'Event deleted successfully'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    def get_calendar_context(self, request):
        # Get the month and year from the request, default to current month
        today = datetime.now()
        month = int(request.GET.get('month', today.month))
        year = int(request.GET.get('year', today.year))
        
        # Get the first and last day of the month
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        
        # Get all plantings for this month
        plantings = PlantingSchedule.objects.filter(
            Q(inside_planting_date__range=(first_day, last_day)) |
            Q(outside_planting_date__range=(first_day, last_day)) |
            Q(harvest_date__range=(first_day, last_day))
        )
        
        if not request.user.is_superuser:
            plantings = plantings.filter(garden_bed__group__in=request.user.groups.all())
        
        # Get the day of the week of the first day (0 = Monday, 6 = Sunday)
        # Convert to Sunday = 0, Monday = 1, etc.
        first_weekday = (first_day.weekday() + 1) % 7
        
        # Create calendar data structure
        calendar_data = {}
        for day in range(1, last_day.day + 1):
            current_date = date(year, month, day)
            calendar_data[day] = {
                'plantings': [],
                'date': current_date
            }
        
        for planting in plantings:
            # Handle inside planting dates
            if planting.inside_planting_date and planting.inside_planting_date.month == month and planting.inside_planting_date.year == year:
                day = planting.inside_planting_date.day
                calendar_data[day]['plantings'].append({
                    'id': planting.id,
                    'plant_name': str(planting.variety) + ' (Qty: ' + str(planting.quantity) + ')',
                    'event_type': 'planting',
                    'status': planting.status,
                    'garden_bed': 'Inside Seed Planting'
                })
            
            # Handle outside planting dates
            if planting.outside_planting_date and planting.outside_planting_date.month == month and planting.outside_planting_date.year == year:
                day = planting.outside_planting_date.day
                calendar_data[day]['plantings'].append({
                    'id': planting.id,
                    'plant_name': str(planting.variety) + ' (Qty: ' + str(planting.quantity) + ')',
                    'event_type': 'transplant',
                    'status': planting.status,
                    'garden_bed': 'Plant Outside :: ' + str(planting.garden_bed)
                })
            
            # Handle harvest dates
            if planting.harvest_date and planting.harvest_date.month == month and planting.harvest_date.year == year:
                day = planting.harvest_date.day
                calendar_data[day]['plantings'].append({
                    'id': planting.id,
                    'plant_name': str(planting.variety),
                    'event_type': 'harvest',
                    'status': planting.status,
                    'garden_bed': str(planting.garden_bed)
                })
        
        # Calculate previous and next month/year
        if month == 1:
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year
            
        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year
        
        # Create calendar weeks
        calendar_weeks = []
        week = [None] * first_weekday
        
        for day in range(1, last_day.day + 1):
            week.append((day, calendar_data.get(day, {'plantings': [], 'date': date(year, month, day)})))
            if len(week) == 7:
                calendar_weeks.append(week)
                week = []
        
        # Pad the last week if necessary
        if week:
            week.extend([None] * (7 - len(week)))
            calendar_weeks.append(week)
        
        return {
            'calendar_weeks': calendar_weeks,
            'month': month,
            'year': year,
            'month_name': calendar.month_name[month],
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
            'today': datetime.now().date(),
            'garden_beds': GardenBed.objects.filter(group__in=request.user.groups.all()) if not request.user.is_superuser else GardenBed.objects.all(),
            'varieties': Variety.objects.all().order_by('variety_name')
        }

    def calendar_view(self, request, for_pdf=False):
        # Get calendar context
        context = self.get_calendar_context(request)
        if for_pdf:
            return context
        return TemplateResponse(request, 'admin/schedule/plantingschedule/calendar.html', context)

    def calendar_pdf_view(self, request):
        # Get the month and year from the request, default to current month
        today = datetime.now()
        month = request.GET.get('month')
        year = request.GET.get('year')
        
        # If no month/year provided in URL, use current month/year
        if not month or not year:
            month = today.month
            year = today.year
        
        # Create a new request with the same month/year
        pdf_request = request.GET.copy()
        pdf_request.update({'month': month, 'year': year})
        request.GET = pdf_request
        
        # Get the same context as the regular calendar view
        context = self.calendar_view(request, for_pdf=True)
        
        # Render the HTML template
        html_string = render_to_string('admin/schedule/plantingschedule/calendar_pdf.html', context)
        
        # Configure fonts
        font_config = FontConfiguration()
        
        # Create PDF
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf(font_config=font_config)
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="garden_calendar_{context["month_name"]}_{context["year"]}.pdf"'
        
        return response

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_calendar_link'] = True
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(garden_bed__group__in=request.user.groups.all())
        return qs
    
    def get_list_filter(self, request):
        list_filter = list(super().get_list_filter(request))
        if not request.user.is_superuser:
            list_filter.remove('garden_bed')
        return list_filter

    # AJAX view to calculate planting dates based on harvest date
    def calculate_dates(self, request, object_id=None):
        if request.method == 'POST':
            try:
                harvest_date_str = request.POST.get('harvest_date')
                variety_id = request.POST.get('variety_id')
                
                if not harvest_date_str or not variety_id:
                    return JsonResponse({'error': 'Missing required parameters'}, status=400)
                    
                harvest_date = datetime.strptime(harvest_date_str, '%Y-%m-%d').date()
                variety = Variety.objects.get(id=variety_id)
                
                # Create a temporary PlantingSchedule object to use its calculate_dates_from_harvest method
                temp_schedule = PlantingSchedule(variety=variety)
                dates = temp_schedule.calculate_dates_from_harvest(harvest_date)
                
                return JsonResponse({
                    'inside_planting_date': dates['inside_planting_date'].isoformat() if dates['inside_planting_date'] else None,
                    'outside_planting_date': dates['outside_planting_date'].isoformat() if dates['outside_planting_date'] else None,
                    'harvest_date': dates['harvest_date'].isoformat()
                })
                
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
                
        return JsonResponse({'error': 'Invalid request method'}, status=405)
