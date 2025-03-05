from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Beneficial

class BeneficialListView(LoginRequiredMixin, ListView):
    model = Beneficial
    template_name = 'beneficials/beneficial_list.html'
    context_object_name = 'beneficials'

    def get_queryset(self):
        return Beneficial.objects.filter(group__in=self.request.user.groups.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'beneficials'
        context['page_name'] = 'beneficials'
        context['page_action'] = 'list'
        return context

class BeneficialCreateView(LoginRequiredMixin, CreateView):
    model = Beneficial
    template_name = 'beneficials/beneficial_form.html'
    fields = ['name', 'species', 'type', 'active_from_month', 'active_to_month', 'benefits', 'photo']
    success_url = reverse_lazy('beneficials:list')

    def form_valid(self, form):
        form.instance.group = self.request.user.groups.first()
        messages.success(self.request, 'Beneficial organism added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'beneficials'
        context['page_name'] = 'beneficials'
        context['page_action'] = 'form'
        return context

class BeneficialUpdateView(LoginRequiredMixin, UpdateView):
    model = Beneficial
    template_name = 'beneficials/beneficial_form.html'
    fields = ['name', 'species', 'type', 'active_from_month', 'active_to_month', 'benefits', 'photo']
    context_object_name = 'beneficial'
    success_url = reverse_lazy('beneficials:list')

    def get_queryset(self):
        return Beneficial.objects.filter(group__in=self.request.user.groups.all())

    def form_valid(self, form):
        messages.success(self.request, 'Beneficial organism updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'beneficials'
        context['page_name'] = 'beneficials'
        context['page_action'] = 'form'
        return context

class BeneficialDeleteView(LoginRequiredMixin, DeleteView):
    model = Beneficial
    success_url = reverse_lazy('beneficials:list')

    def get_queryset(self):
        return Beneficial.objects.filter(group__in=self.request.user.groups.all())

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Beneficial organism deleted successfully.')
        return super().delete(request, *args, **kwargs)
