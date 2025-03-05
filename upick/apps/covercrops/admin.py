from django.contrib import admin
from .models import CoverCropMix, CoverCropPlantComponent, CoverCropPlan

class CoverCropPlantComponentInline(admin.TabularInline):
    model = CoverCropPlantComponent
    extra = 1
    min_num = 1

@admin.register(CoverCropMix)
class CoverCropMixAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    inlines = [CoverCropPlantComponentInline]
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CoverCropPlan)
class CoverCropPlanAdmin(admin.ModelAdmin):
    filter_horizontal = ('attracted_beneficials',)
    list_display = (
        'name',
        'mix',
        'planting_season',
        'planting_window_start',
        'planting_window_end',
        'termination_method',
        'get_attracted_beneficials'
    )
    list_filter = (
        'planting_season',
        'frost_tolerant',
        'drought_tolerant',
        'nitrogen_fixer',
        'beneficial_insect',
        'termination_method'
    )
    search_fields = ('name', 'description', 'mix__name', 'attracted_beneficials__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'mix')
        }),
        ('Timing', {
            'fields': (
                'planting_season',
                'planting_window_start',
                'planting_window_end',
                'weeks_to_grow'
            )
        }),
        ('Growing Conditions', {
            'fields': (
                'minimum_soil_temp',
                'frost_tolerant',
                'drought_tolerant'
            )
        }),
        ('Benefits', {
            'fields': (
                'nitrogen_fixer',
                'biomass_producer',
                'weed_suppressor',
                'erosion_controller',
                'beneficial_insect',
                'attracted_beneficials'
            ),
            'description': 'Select the benefits provided by this cover crop plan. If it attracts beneficial organisms, mark "beneficial_insect" and select the specific organisms below.'
        }),
        ('Termination', {
            'fields': (
                'termination_method',
                'days_before_cash_crop'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_attracted_beneficials(self, obj):
        return ", ".join([b.name for b in obj.attracted_beneficials.all()])
    get_attracted_beneficials.short_description = 'Attracted Beneficials'
