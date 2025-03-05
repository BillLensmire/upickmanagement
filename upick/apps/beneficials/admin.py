from django.contrib import admin
from django.utils.html import format_html
from .models import Beneficial

@admin.register(Beneficial)
class BeneficialAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'species', 'active_period', 'photo_preview']
    list_filter = ['type', 'active_from_month', 'active_to_month']
    search_fields = ['name', 'species', 'benefits']
    readonly_fields = ['created_at', 'updated_at', 'photo_preview']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'species', 'type']
        }),
        ('Seasonal Activity', {
            'fields': ['active_from_month', 'active_to_month']
        }),
        ('Details', {
            'fields': ['benefits', 'photo', 'photo_preview']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

    def active_period(self, obj):
        months = dict(Beneficial.MONTH_CHOICES)
        return f"{months[obj.active_from_month]} - {months[obj.active_to_month]}"
    active_period.short_description = 'Active Period'

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 50px;"/>',
                obj.photo.url
            )
        return "-"
    photo_preview.short_description = 'Photo'
