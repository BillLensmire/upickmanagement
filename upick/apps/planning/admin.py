from django.contrib import admin

from .models import (
    GardenConfiguration,
    GardenPlan,
    SeedSource,
    SeedInventory,
    CropRotationRule,
    SeedSourceDocument
)
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
import os

@admin.register(GardenConfiguration)
class GardenConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Garden Bed Defaults', {
            'fields': ('default_bed_length', 'default_bed_width')
        }),
        ('Growing Season', {
            'fields': ('spring_frost_date', 'fall_frost_date', 'growing_zone')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        # Only allow adding if no configuration exists
        return not GardenConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the configuration
        return False

@admin.register(SeedSource)
class SeedSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name', 'website', 'notes')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SeedInventory)
class SeedInventoryAdmin(admin.ModelAdmin):
    list_display = ('plant', 'source', 'purchase_date', 'packet_size', 'seeds_remaining', 'cost')
    list_filter = ('source', 'purchase_date', 'expiration_date')
    search_fields = ('plant__name', 'source__name', 'lot_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('plant', 'source', 'purchase_date')
        }),
        ('Packet Details', {
            'fields': ('lot_number', 'packet_size', 'seeds_per_packet', 'cost')
        }),
        ('Germination Information', {
            'fields': ('germination_rate', 'germination_test_date', 'expiration_date')
        }),
        ('Inventory', {
            'fields': ('seeds_remaining', 'notes')
        })
    )

@admin.register(GardenPlan)
class GardenPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'year')
    list_filter = ('year', 'group')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CropRotationRule)
class CropRotationRuleAdmin(admin.ModelAdmin):
    list_display = ('plant_family', 'years_before_repeat')
    search_fields = ('plant_family', 'notes')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SeedSourceDocument)
class SeedSourceDocumentAdmin(admin.ModelAdmin):
    list_display = ('description_link', 'file_link', 'seed_source', 'uploaded_at')
    list_filter = ('seed_source', 'uploaded_at')
    search_fields = ('description', 'seed_source__name')
    date_hierarchy = 'uploaded_at'

    def file_link(self, obj):
        urlstr = "seed-documents/" + str(obj.id)
        fname = os.path.basename(obj.file.name)
        rtnstr = format_html('<a href="{0}" target="_blank">{1}</a>', urlstr, fname)
        return rtnstr
    file_link.short_description = 'File'

    def description_link(self, obj):
        urlstr = "seed-documents/" + str(obj.id)
        fname = os.path.basename(obj.file.name)
        rtnstr = format_html('<a href="{0}" target="_blank">{1}</a>', urlstr, obj.short_description)
        return rtnstr
    description_link.short_description = 'Description'

    def view_seed_source_document(self, request, pk):
        document = get_object_or_404(SeedSourceDocument, pk=pk)
        return FileResponse(document.file)


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('seed-documents/<int:pk>/', self.admin_site.admin_view(self.view_seed_source_document), name='view_seed_source_document'),
            path('seed-documents/<int:pk>/change/', self.admin_site.admin_view(self.view_seed_source_document), name='view_seed_source_document'),
        ]
        return custom_urls + urls
