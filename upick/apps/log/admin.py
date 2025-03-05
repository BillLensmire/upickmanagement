from django.contrib import admin
from .models import LogEntry

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = [
        'entry_type',
        'title',
        'logdate',
        'get_short_text',
        'has_photo',
        'has_document',
        'created_at'
    ]
    list_filter = [
        'entry_type',
        'logdate',
        'plants',
        'plant_schedule',
        'foliar_recipe',
        'cover_crop',
        'beneficial',
        'garden_bed',
        'seed_source',
    ]
    search_fields = [
        'description',
        'plants__name',
        'plant_schedule__name',
        'foliar_recipe__name',
        'cover_crop__name',
        'beneficial__name',
        'garden_bed__name',
        'seed_source__name',
    ]
    date_hierarchy = 'logdate'
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['plants']
    
    def get_short_text(self, obj):
        """Return truncated text entry for list display"""
        if len(obj.description) > 50:
            return f"{obj.description[:47]}..."
        return obj.description
    get_short_text.short_description = 'Text Entry'
    
    def has_photo(self, obj):
        """Return whether entry has a photo"""
        return bool(obj.photo)
    has_photo.boolean = True
    has_photo.short_description = 'Has Photo'
    
    def has_document(self, obj):
        """Return whether entry has a document"""
        return bool(obj.document)
    has_document.boolean = True
    has_document.short_description = 'Has Document'
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['entry_type', 'logdate', 'description']
        }),
        ('Attachments', {
            'fields': ['photo', 'document'],
            'classes': ['collapse']
        }),
        ('Related Items', {
            'fields': [
                'plants',
                'plant_schedule',
                'foliar_recipe',
                'cover_crop',
                'beneficial',
                'garden_bed',
                'seed_source'
            ],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
