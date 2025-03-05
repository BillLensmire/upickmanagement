from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import Group
from datetime import datetime
from .models import  GardenPlan
from .forms import GardenPlanForm

def get_user_group(request):
    """Get the user's active group or return None if user has no groups.
    Also adds an error message if the user has no groups.
    """
    if not request.user.groups.exists():
        messages.error(request, 'You must be a member of at least one group to perform this action. Please contact your administrator.')
        return None
    return request.user.groups.first()

# Garden Plan Views
class GardenPlanListView(LoginRequiredMixin, ListView):
    model = GardenPlan
    template_name = 'planning/garden_plan_list.html'
    context_object_name = 'garden_plans'

    def get_queryset(self):
        return GardenPlan.objects.filter(group__in=self.request.user.groups.all()).order_by('year', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'planning'
        context['page_name'] = 'garden_plan'
        context['page_action'] = 'list'
        return context

class GardenPlanCreateView(LoginRequiredMixin, CreateView):
    model = GardenPlan
    template_name = 'planning/garden_plan_form.html'
    form_class = GardenPlanForm
    success_url = reverse_lazy('planning:garden_plan_list')

    def get_initial(self):
        # Set default year to current year
        return {'year': datetime.now().year}

    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a garden plan.')
            return self.form_invalid(form)
        form.instance.group = group
        messages.success(self.request, 'Garden plan created successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, f'Error creating garden plan: {form.errors}')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'planning'
        context['page_name'] = 'garden_plan'
        context['page_action'] = 'form'
        context['groups'] = Group.objects.all()
        return context

class GardenPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = GardenPlan
    template_name = 'planning/garden_plan_form.html'
    form_class = GardenPlanForm
    context_object_name = 'garden_plan'
    success_url = reverse_lazy('planning:garden_plan_list')

    def get_queryset(self):
        return GardenPlan.objects.filter(group__in=self.request.user.groups.all())

    def form_valid(self, form):
        messages.success(self.request, 'Garden plan updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'planning'
        context['page_name'] = 'garden_plan'
        context['page_action'] = 'form'
        return context

    def form_invalid(self, form):
        messages.error(self.request, f'Error updating garden plan: {form.errors}')
        return super().form_invalid(form)

class GardenPlanDetailView(LoginRequiredMixin, DetailView):
    model = GardenPlan
    template_name = 'planning/garden_plan_detail.html'
    context_object_name = 'garden_plan'

    def get_queryset(self):
        return GardenPlan.objects.filter(group__in=self.request.user.groups.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        garden_plan = self.get_object()
        context['page_app'] = 'planning'
        context['page_name'] = 'garden_plan'
        context['page_action'] = 'detail'
        # Handle the case where produce_plan_overview might not exist
        context['produce_plan'] = getattr(garden_plan, 'produce_plan_overview', None)
        from schedule.models import GardenBed, PlantingSchedule
        context['garden_beds'] = GardenBed.objects.filter(
            group__in=self.request.user.groups.all(),
            year=garden_plan.year
        )
        context['planting_schedules'] = PlantingSchedule.objects.filter(garden_plan=garden_plan)
        return context

class GardenPlanDeleteView(LoginRequiredMixin, DeleteView):
    model = GardenPlan
    success_url = reverse_lazy('planning:garden_plan_list')

    def get_queryset(self):
        return GardenPlan.objects.filter(group__in=self.request.user.groups.all())

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Garden plan deleted successfully.')
        return super().delete(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Redirect GET requests to the list view
        return redirect('planning:garden_plan_list')
