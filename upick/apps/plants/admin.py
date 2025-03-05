from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from .models import Plant, Variety

# Register your models here.

class VarietyInline(admin.TabularInline):
    model = Variety
    extra = 1
    fields = (
        'variety_name', 
        'variety_planting_method', 
        'variety_spacing_between_plants', 
        'variety_spacing_between_rows',
        'variety_days_to_maturity',
        'variety_days_from_seed_to_transplant',
        'variety_days_from_frost_to_transplant',
    )

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'seed_type', 'planting_method', 'days_to_maturity', 'is_perennial')
    list_filter = (
        'seed_type',
        'planting_method',
        'is_perennial'
    )
    search_fields = (
        'name',
        'description'
    )
    
    inlines = [VarietyInline]
    actions = ['duplicate_plants', 'duplicate_and_edit_plant']
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'description',
                'seed_type',
                'is_perennial',
                'group',
                'research_notes'
            )
        }),
        ('Planting Specifications', {
            'fields': (
                'planting_method',
                'spacing_between_plants',
                'spacing_between_rows'
            )
        }),
        ('Temperature and Timing', {
            'fields': (
                ('germination_temp_min', 'germination_temp_max'),
                'days_to_germinate',
                'days_to_maturity',
                'days_from_seed_to_transplant',
                'days_from_frost_to_transplant'
            )
        }),
        ('Plant Characteristics', {
            'fields': (
                'height_inches',
            )
        }),
        ('Relationships', {
            'fields': (
                'companion_plants',
            ),
            'classes': ('collapse',)
        })
    )
    
    filter_horizontal = ('companion_plants',)
    readonly_fields = ('created_at', 'updated_at')

    def duplicate_plant(self, plant):
        """Helper method to duplicate a plant and return the new instance"""
        # Create a copy of the plant
        plant.pk = None  # This will create a new instance
        plant.name = f"{plant.name} (Copy)"
        plant.save()
        
        # Copy many-to-many relationships
        original_plant = Plant.objects.get(pk=plant.pk)
        plant.companion_plants.set(original_plant.companion_plants.all())
        
        return plant

    def duplicate_plants(self, request, queryset):
        for plant in queryset:
            new_plant = self.duplicate_plant(plant)
            messages.success(request, f'Successfully duplicated "{plant.name}"')
    
    duplicate_plants.short_description = "Duplicate selected plants"

    def duplicate_and_edit_plant(self, request, queryset):
        if len(queryset) != 1:
            messages.error(request, "Please select exactly one plant to duplicate and edit.")
            return
        
        # Duplicate the selected plant
        original_plant = queryset.first()
        new_plant = self.duplicate_plant(original_plant)
        
        # Redirect to the edit page of the new plant
        url = reverse(
            f'admin:{new_plant._meta.app_label}_{new_plant._meta.model_name}_change',
            args=[new_plant.pk]
        )
        return redirect(url)
    
    duplicate_and_edit_plant.short_description = "Duplicate and edit plant"
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make certain fields required even though they can be null in the database
        required_fields = [
            'spacing_between_plants',
            'spacing_between_rows',
            'days_to_maturity',
            'height_inches'
        ]
        for field_name in required_fields:
            if field_name in form.base_fields:
                form.base_fields[field_name].required = True
        return form
    
    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }
        js = ('admin/js/core.js',)

@admin.register(Variety)
class VarietyAdmin(admin.ModelAdmin):
    list_display = ('variety_name', 'variety_plant', 'variety_planting_method', 'variety_days_to_maturity')
    list_filter = ('variety_planting_method', 'variety_planting_season')
    search_fields = ('variety_name', 'variety_description', 'scientific_name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'variety_plant',
                'variety_name',
                'scientific_name',
                'variety_description',
            )
        }),
        ('Planting Specifications', {
            'fields': (
                'variety_planting_method',
                'variety_spacing_between_plants',
                'variety_spacing_between_rows'
            )
        }),
        ('Timing', {
            'fields': (
                'variety_days_to_maturity',
                'variety_days_from_seed_to_transplant',
                'variety_days_from_frost_to_transplant',
                'variety_planting_season'
            )
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make certain fields required even though they can be null in the database
        required_fields = [
            'variety_plant',
            'variety_name'
        ]
        for field_name in required_fields:
            if field_name in form.base_fields:
                form.base_fields[field_name].required = True
        return form
