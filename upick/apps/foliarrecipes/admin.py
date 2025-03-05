from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from .models import (
    MineralRaw, Supplier, SupplierMineralProduct, SupplierChelatingProduct,
    ChelatingAgent, ChelatedMineral, FoliarRecipe, RecipeIngredient,
    PurchasedProduct, FoliarApplication, FoliarSchedule, RecipeIngredientRelationship
)

class SupplierMineralProductInline(admin.TabularInline):
    model = SupplierMineralProduct
    extra = 1
    fields = ('supplier', 'package_size', 'package_unit', 'price', 'minimum_order', 'url')

class SupplierChelatingProductInline(admin.TabularInline):
    model = SupplierChelatingProduct
    extra = 1
    fields = ('supplier', 'package_size', 'package_unit', 'price', 'minimum_order', 'url')

@admin.register(MineralRaw)
class MineralRawAdmin(admin.ModelAdmin):
    list_display = ('name', 'mineral', 'form', 'mineral_content', 'solubility', 'ph_range')
    list_filter = ('mineral', 'form')
    search_fields = ('name', 'mineral', 'chemical_formula')
    inlines = [SupplierMineralProductInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'mineral', 'form', 'chemical_formula')
        }),
        ('Properties', {
            'fields': ('mineral_content', 'solubility', 'ph_range')
        }),
        ('Notes', {
            'fields': ('notes',)
        })
    )

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_name', 'contact_email', 'contact_phone', 'website_link')
    search_fields = ('name', 'contact_name', 'contact_email')
    
    def website_link(self, obj):
        if obj.website:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website)
        return "-"
    website_link.short_description = "Website"

@admin.register(ChelatingAgent)
class ChelatingAgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'form', 'optimal_ph_range', 'solubility')
    list_filter = ('form',)
    search_fields = ('name', 'chemical_formula')
    inlines = [SupplierChelatingProductInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'form', 'chemical_formula')
        }),
        ('Properties', {
            'fields': ('optimal_ph_range', 'solubility', 'stability_notes')
        }),
        ('Notes', {
            'fields': ('notes',)
        })
    )

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredientRelationship
    extra = 1
    fields = ('ingredient', 'order')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "ingredient":
            kwargs["queryset"] = RecipeIngredient.objects.filter(group__in=request.user.groups.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class FoliarApplicationInline(admin.TabularInline):
    model = FoliarApplication
    extra = 0
    fields = ('application_date', 'application_time', 'area_treated', 'actual_amount', 'effectiveness_rating')
    ordering = ('-application_date', '-application_time')

class FoliarScheduleInline(admin.TabularInline):
    model = FoliarSchedule
    extra = 0
    fields = ('start_date', 'preferred_time', 'repeat_pattern', 'area_to_treat', 'status')
    ordering = ('start_date', 'preferred_time')

@admin.register(ChelatedMineral)
class ChelatedMineralAdmin(admin.ModelAdmin):
    list_display = ('name', 'mineral_raw', 'chelating_agent', 'ph_target', 'temperature')
    list_filter = ('mineral_raw__mineral', 'chelating_agent')
    search_fields = ('name', 'mineral_raw__name', 'chelating_agent__name')
    fieldsets = (
        (None, {
            'fields': ('name', 'mineral_raw', 'mineral_amount')
        }),
        ('Chelation Process', {
            'fields': ('water_amount', 'ph_target', 'temperature', 'chelating_agent', 'chelating_agent_amount')
        }),
        ('Process & Notes', {
            'fields': ('process', 'notes')
        })
    )

@admin.register(FoliarRecipe)
class FoliarRecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'growth_stage', 'target_ph', 'application_frequency', 'last_application')
    list_filter = ('growth_stage',)
    search_fields = ('name', 'description')
    inlines = [RecipeIngredientInline, FoliarScheduleInline, FoliarApplicationInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'growth_stage')
        }),
        ('Application Details', {
            'fields': ('base_water_amount', 'target_ph', 'application_frequency', 'best_time')
        }),
        ('Conditions & Process', {
            'fields': ('process', 'notes')
        })
    )

    def last_application(self, obj):
        last_app = obj.applications.order_by('-application_date', '-application_time').first()
        if last_app:
            return last_app.application_date
        return "-"
    last_application.short_description = "Last Applied"

@admin.register(PurchasedProduct)
class PurchasedProductAdmin(admin.ModelAdmin):
    list_display = ('supplier_product', 'purchase_date', 'quantity', 'remaining_quantity', 'storage_location', 'is_low_stock')
    list_filter = ('supplier_product__supplier', 'storage_location', 'purchase_date')
    search_fields = ('supplier_product__mineral_raw__name', 'lot_number', 'storage_location')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('supplier_product', 'purchase_date', 'quantity', 'package_size', 'package_unit')
        }),
        ('Cost', {
            'fields': ('price_paid', 'shipping_cost')
        }),
        ('Inventory', {
            'fields': ('remaining_quantity', 'storage_location', 'lot_number', 'expiration_date')
        }),
        ('Additional Info', {
            'fields': ('purchase_order', 'notes')
        })
    )
    
    def is_low_stock(self, obj):
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = "Low Stock"

@admin.register(FoliarApplication)
class FoliarApplicationAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'application_date', 'application_time', 'area_treated', 'actual_amount', 'effectiveness_rating')
    list_filter = ('recipe', 'application_date', 'effectiveness_rating')
    search_fields = ('recipe__name', 'area_treated', 'observations')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('recipe', 'application_date', 'application_time')
        }),
        ('Application Details', {
            'fields': ('area_treated', 'actual_amount', 'best_time')
        }),
        ('Results', {
            'fields': ('effectiveness_rating', 'observations')
        }),
        ('Conditions & Process', {
            'fields': ('process', 'notes') 
        })
    )

@admin.register(FoliarSchedule)
class FoliarScheduleAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'start_date', 'preferred_time', 'repeat_pattern', 'area_to_treat', 'status', 'next_date', 'is_active')
    list_filter = ('status', 'repeat_pattern', 'recipe')
    search_fields = ('recipe__name', 'area_to_treat', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('recipe', 'status')
        }),
        ('Schedule Details', {
            'fields': ('start_date', 'end_date', 'preferred_time', 'repeat_pattern', 'custom_days')
        }),
        ('Application Details', {
            'fields': ('area_to_treat', 'planned_amount', 'best_time')
        }),
        ('Notes', {
            'fields': ('notes',)
        })
    )

    def next_date(self, obj):
        next_date = obj.next_application_date()
        if next_date:
            if next_date < now().date():
                return format_html('<span style="color: red;">{}</span>', next_date)
            return next_date
        return "-"
    next_date.short_description = "Next Application"

    def is_active(self, obj):
        return obj.is_active()
    is_active.boolean = True
    is_active.short_description = "Active"
