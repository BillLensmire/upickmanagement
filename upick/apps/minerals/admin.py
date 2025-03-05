from django.contrib import admin
from .models import MineralNutrient, PlantNutrientRequirement, NutrientNote, MineralUrl

# Register your models here.

@admin.register(MineralNutrient)
class MineralNutrientAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'symbol', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'symbol', 'category','description')
        }),
        ('Plant Health Information', {
            'fields': ('function', 'deficiency_symptoms', 'excess_symptoms')
        }),
        ('Soil and Application', {
            'fields': ('optimal_soil_ph', 'sources', 'application_methods', 'application_rate')
        }),
        ('Interactions', {
            'fields': ('interactions',)
        }),
    )

@admin.register(PlantNutrientRequirement)
class PlantNutrientRequirementAdmin(admin.ModelAdmin):
    list_display = ('plant_type', 'nutrient', 'requirement_level', 'critical_points_of_influence')
    list_filter = ('requirement_level', 'nutrient', 'critical_points_of_influence')
    search_fields = ('plant_type', 'notes', 'critical_points_of_influence')


@admin.register(NutrientNote)
class NutrientNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'nutrient', 'source', 'created_at')
    list_filter = ('nutrient', 'created_at')
    search_fields = ('title', 'content', 'source')
    date_hierarchy = 'created_at'

@admin.register(MineralUrl)
class MineralUrlAdmin(admin.ModelAdmin):
    list_display = ('mineral', 'url', 'created_at')
    list_filter = ('mineral', 'created_at')
    search_fields = ('mineral__name', 'url')
    date_hierarchy = 'created_at'