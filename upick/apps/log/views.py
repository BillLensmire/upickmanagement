from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.models import Group
from .models import LogEntry
from django.db.models import Q
from apps.plants.models import Plant
from apps.beneficials.models import Beneficial
from apps.planning.models import GardenPlan, SeedSource
from apps.foliarrecipes.models import FoliarRecipe
from apps.schedule.models import GardenBed
from datetime import date

def get_user_group(request):
    """Get the user's active group or return None if user has no groups.
    Also adds an error message if the user has no groups.
    """
    if not request.user.groups.exists():
        messages.error(request, 'You must be a member of at least one group to perform this action. Please contact your administrator.')
        return None
    return request.user.groups.first()
    
@login_required
def log_list(request):
    entry_type = request.GET.get('type', '')
    search_query = request.GET.get('search', '')
    
    logs = LogEntry.objects.all().order_by('-created_at')
    
    if entry_type:
        logs = logs.filter(entry_type=entry_type)
    
    if search_query:
        logs = logs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(logs, 10)  # Show 10 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Sort entry types by display name
    sorted_entry_types = sorted(LogEntry.ENTRY_TYPE_CHOICES, key=lambda x: x[1])
    
    context = {
        'page_obj': page_obj,
        'entry_types': sorted_entry_types,
        'current_type': entry_type,
        'search_query': search_query,
    }
    return render(request, 'log/log_list.html', context)

@login_required
def log_detail(request, pk):
    log_entry = get_object_or_404(LogEntry, pk=pk)
    return render(request, 'log/log_detail.html', {'log_entry': log_entry})

@login_required
def log_create(request):
    if request.method == 'POST':
        # Handle form submission
        entry_type = request.POST.get('entry_type')
        title = request.POST.get('title')
        description = request.POST.get('description')
        logdate = date.today()
        
        group = get_user_group(request)
        if not group:
            group = Group.objects.get(name='Default')

        if title and entry_type:
            # Create log entry
            log_entry = LogEntry.objects.create(
                entry_type=entry_type,
                title=title,
                description=description,
                logdate=logdate,
                group=group
            )
            
            # Handle file uploads
            if 'photo' in request.FILES:
                log_entry.photo = request.FILES['photo']
            if 'document' in request.FILES:
                log_entry.document = request.FILES['document']
            
            # Handle related fields
            plant_ids = request.POST.getlist('plants')
            if plant_ids:
                log_entry.plants.clear()
                log_entry.plants.add(*Plant.objects.filter(id__in=plant_ids))

            # Handle single foreign key fields
            if request.POST.get('plant_schedule'):
                try:
                    log_entry.plant_schedule = GardenPlan.objects.get(id=request.POST['plant_schedule'])
                except GardenPlan.DoesNotExist:
                    log_entry.plant_schedule = None
            
            if request.POST.get('foliar_recipe'):
                try:
                    log_entry.foliar_recipe = FoliarRecipe.objects.get(id=request.POST['foliar_recipe'])
                except FoliarRecipe.DoesNotExist:
                    log_entry.foliar_recipe = None
            
            if request.POST.get('cover_crop'):
                try:
                    log_entry.cover_crop = Plant.objects.get(id=request.POST['cover_crop'])
                except Plant.DoesNotExist:
                    log_entry.cover_crop = None
            
            if request.POST.get('beneficial'):
                try:
                    log_entry.beneficial = Beneficial.objects.get(id=request.POST['beneficial'])
                except Beneficial.DoesNotExist:
                    log_entry.beneficial = None
            
            if request.POST.get('garden_bed'):
                try:
                    log_entry.garden_bed = GardenBed.objects.get(id=request.POST['garden_bed'])
                except GardenBed.DoesNotExist:
                    log_entry.garden_bed = None
            
            if request.POST.get('seed_source'):
                try:
                    log_entry.seed_source = SeedSource.objects.get(id=request.POST['seed_source'])
                except SeedSource.DoesNotExist:
                    log_entry.seed_source = None
        
            if request.POST.get('garden_plan'):
                try:
                    log_entry.garden_plan = GardenPlan.objects.get(id=request.POST['garden_plan'])
                except GardenPlan.DoesNotExist:
                    log_entry.garden_plan = None
            
            # Save the files
            log_entry.save()
            
            messages.success(request, 'Log entry created successfully!')
            return redirect('log:log_detail', pk=log_entry.pk)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'entry_types': sorted(LogEntry.ENTRY_TYPE_CHOICES, key=lambda x: x[1]),  # Sort by display name
        'garden_plans': GardenPlan.objects.all(),
        'foliar_recipes': FoliarRecipe.objects.all(),
        'beneficials': Beneficial.objects.all(),
        'garden_beds': GardenBed.objects.all(),
        'seed_sources': SeedSource.objects.all(),
        'groups': Group.objects.all(),
    }
    return render(request, 'log/log_form.html', context)

@login_required
def log_edit(request, pk):
    log_entry = get_object_or_404(LogEntry, pk=pk)
    
    if request.method == 'POST':
        # Basic fields
        entry_type = request.POST.get('entry_type')
        title = request.POST.get('title')
        description = request.POST.get('description')
        logdate = date.today()
        
        # Validate required fields
        if not all([title, entry_type]):
            messages.error(request, 'Please fill in all required fields.')
            # Sort entry types by display name
            sorted_entry_types = sorted(LogEntry.ENTRY_TYPE_CHOICES, key=lambda x: x[1])
            
            context = {
                'log_entry': log_entry,
                'entry_types': sorted_entry_types,
                'plants': Plant.objects.all(),
                'garden_plans': GardenPlan.objects.all(),
                'foliar_recipes': FoliarRecipe.objects.all(),
                'beneficials': Beneficial.objects.all(),
                'garden_beds': GardenBed.objects.all(),
                'seed_sources': SeedSource.objects.all(),
                'groups': Group.objects.all(),
            }
            return render(request, 'log/log_form.html', context)
        
        # Update basic fields
        log_entry.entry_type = entry_type
        log_entry.title = title
        log_entry.description = description
        log_entry.logdate = logdate
        
        # Handle file uploads
        if 'photo' in request.FILES:
            # Delete old photo if it exists
            if log_entry.photo:
                log_entry.photo.delete(save=False)
            log_entry.photo = request.FILES['photo']
            
        if 'document' in request.FILES:
            # Delete old document if it exists
            if log_entry.document:
                log_entry.document.delete(save=False)
            log_entry.document = request.FILES['document']
        
        # Handle group
        group_id = request.POST.get('group')
        if group_id:
            try:
                log_entry.group = Group.objects.get(id=group_id)
            except Group.DoesNotExist:
                pass
        
        # Handle related fields
        plant_ids = request.POST.getlist('plants')
        if plant_ids:
            log_entry.plants.clear()
            log_entry.plants.add(*Plant.objects.filter(id__in=plant_ids))
        
        # Handle single foreign key fields
        if request.POST.get('plant_schedule'):
            try:
                log_entry.plant_schedule = GardenPlan.objects.get(id=request.POST['plant_schedule'])
            except GardenPlan.DoesNotExist:
                log_entry.plant_schedule = None
        
        if request.POST.get('foliar_recipe'):
            try:
                log_entry.foliar_recipe = FoliarRecipe.objects.get(id=request.POST['foliar_recipe'])
            except FoliarRecipe.DoesNotExist:
                log_entry.foliar_recipe = None
        
        if request.POST.get('cover_crop'):
            try:
                log_entry.cover_crop = Plant.objects.get(id=request.POST['cover_crop'])
            except Plant.DoesNotExist:
                log_entry.cover_crop = None
        
        if request.POST.get('beneficial'):
            try:
                log_entry.beneficial = Beneficial.objects.get(id=request.POST['beneficial'])
            except Beneficial.DoesNotExist:
                log_entry.beneficial = None
        
        if request.POST.get('garden_bed'):
            try:
                log_entry.garden_bed = GardenBed.objects.get(id=request.POST['garden_bed'])
            except GardenBed.DoesNotExist:
                log_entry.garden_bed = None
        
        if request.POST.get('seed_source'):
            try:
                log_entry.seed_source = SeedSource.objects.get(id=request.POST['seed_source'])
            except SeedSource.DoesNotExist:
                log_entry.seed_source = None
        
            if request.POST.get('garden_plan'):
                try:
                    log_entry.garden_plan = GardenPlan.objects.get(id=request.POST['garden_plan'])
                except GardenPlan.DoesNotExist:
                    log_entry.garden_plan = None

        # Save all changes
        log_entry.save()
        messages.success(request, 'Log entry updated successfully!')
        return redirect('log:log_detail', pk=pk)
    
    # GET request - show form
    # Sort entry types by display name
    sorted_entry_types = sorted(LogEntry.ENTRY_TYPE_CHOICES, key=lambda x: x[1])
    
    context = {
        'log_entry': log_entry,
        'entry_types': sorted_entry_types,
        'plants': Plant.objects.filter(group__in=request.user.groups.all()),
        'garden_plans': GardenPlan.objects.filter(group__in=request.user.groups.all()),
        'foliar_recipes': FoliarRecipe.objects.filter(group__in=request.user.groups.all()),
        'beneficials': Beneficial.objects.filter(group__in=request.user.groups.all()),
        'garden_beds': GardenBed.objects.filter(group__in=request.user.groups.all()),
        'seed_sources': SeedSource.objects.filter(group__in=request.user.groups.all()),
        'groups': Group.objects.all(),
    }
    return render(request, 'log/log_form.html', context)
