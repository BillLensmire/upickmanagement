from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import redirect
from datetime import timedelta
from .models import ProducePlan, ProducePlanOverview
from apps.planning.models import GardenConfiguration

@admin.register(ProducePlan)
class ProducePlanAdmin(admin.ModelAdmin):
    list_display = ('plant', 'produce_plan_overview', 'variety', 'group')
    list_filter = ('produce_plan_overview', 'plant')
    search_fields = ('plant__name', 'produce_plan_overview__name')
    actions = ['duplicate_and_edit']

    def duplicate_and_edit(self, request, queryset):
        # Create a copy of each selected plan
        new_plans = []
        for plan in queryset:
            new_plan = ProducePlan.objects.create(
                plant=plan.plant,
                produce_plan_overview=plan.produce_plan_overview,
                group=plan.group,
                variety=plan.variety
            )
            new_plans.append(new_plan)

        # If only one plan was duplicated, redirect to its edit page
        if len(new_plans) == 1:
            return redirect(
                reverse(
                    f'admin:produceplanner_produceplan_change',
                    args=[new_plans[0].id]
                )
            )
        
        # If multiple plans were duplicated, show a message and stay on the list page
        self.message_user(request, f"{len(new_plans)} plans were duplicated.")
    
    duplicate_and_edit.short_description = "Duplicate and edit selected plans"

    class Media:
        js = ['admin/js/jquery.init.js', 'produceplanner/js/admin.js']

@admin.register(ProducePlanOverview)
class ProducePlanOverviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'overall_start_date', 'overall_end_date', 'report_link')
    list_filter = ('group',)
    search_fields = ('name',)

    def report_link(self, obj):
        url = reverse('produceplanner:produce_availability_report', args=[obj.id])
        return format_html('<a href="{}">View You Pick Produce Availability</a>', url)
    report_link.short_description = 'Report'