from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import MineralRaw, Supplier, SupplierMineralProduct, SupplierChelatingProduct, ChelatingAgent, ChelatedMineral, RecipeIngredient
from django.contrib import messages
from django.contrib.auth.models import Group

def get_user_group(request):
    """Get the user's active group or return None if user has no groups.
    Also adds an error message if the user has no groups.
    """
    if not request.user.groups.exists():
        messages.error(request, 'You must be a member of at least one group to perform this action. Please contact your administrator.')
        return None
    return request.user.groups.first()
    
class MineralRawListView(LoginRequiredMixin, ListView):
    model = MineralRaw
    context_object_name = 'mineralraws'
    template_name = 'foliarrecipes/mineralraw_list.html'
    
    def get_queryset(self):
        # Filter by user's group if group is set
        queryset = super().get_queryset()
        if self.request.user.groups.exists():
            return queryset.filter(group__in=self.request.user.groups.all())
        return queryset.filter(group__isnull=True)

class MineralRawDetailView(LoginRequiredMixin, DetailView):
    model = MineralRaw
    context_object_name = 'mineralraw'
    template_name = 'foliarrecipes/mineralraw_detail.html'

class MineralRawCreateView(LoginRequiredMixin, CreateView):
    model = MineralRaw
    template_name = 'foliarrecipes/mineralraw_form.html'
    fields = ['name', 'mineral', 'form', 'chemical_formula', 'mineral_content', 
              'solubility', 'ph_range', 'notes']
    success_url = reverse_lazy('foliarrecipes:mineralraw_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'mineralraws'
        context['page_action'] = 'form'
        context['groups'] = Group.objects.all()
        return context
        
    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a garden plan.')
            return self.form_invalid(form)
        response = super().form_valid(form)
        instance = form.save(commit=False)
        instance.group = group
        instance.save()
        return response

class MineralRawUpdateView(LoginRequiredMixin, UpdateView):
    model = MineralRaw
    template_name = 'foliarrecipes/mineralraw_form.html'
    fields = ['name', 'mineral', 'form', 'chemical_formula', 'mineral_content', 
              'solubility', 'ph_range', 'notes']
    success_url = reverse_lazy('foliarrecipes:mineralraw_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'mineralraws'
        context['page_action'] = 'form'
        return context
        
    def form_valid(self, form):
        # Set the group if user belongs to one 
        if self.request.user.groups.exists():
            form.instance.group = self.request.user.groups.first()
        response = super().form_valid(form)
        return response

class MineralRawDeleteView(LoginRequiredMixin, DeleteView):
    model = MineralRaw
    template_name = 'foliarrecipes/mineralraw_confirm_delete.html'
    success_url = reverse_lazy('foliarrecipes:mineralraw_list')

# Supplier Views
class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    context_object_name = 'suppliers'
    template_name = 'foliarrecipes/supplier_list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.groups.exists():
            return queryset.filter(group__in=self.request.user.groups.all())
        return queryset.filter(group__isnull=True)

class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    context_object_name = 'supplier'
    template_name = 'foliarrecipes/supplier_detail.html'

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    template_name = 'foliarrecipes/supplier_form.html'
    fields = ['name', 'website', 'contact_name', 'contact_email', 'contact_phone',
              'shipping_notes', 'account_number', 'notes']
    success_url = reverse_lazy('foliarrecipes:supplier_list')

    def form_valid(self, form):
        if self.request.user.groups.exists():
            form.instance.group = self.request.user.groups.first()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'suppliers'
        context['page_action'] = 'form'
        return context

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    template_name = 'foliarrecipes/supplier_form.html'
    fields = ['name', 'website', 'contact_name', 'contact_email', 'contact_phone',
              'shipping_notes', 'account_number', 'notes']
    success_url = reverse_lazy('foliarrecipes:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'suppliers'
        context['page_action'] = 'form'
        return context

class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'foliarrecipes/supplier_confirm_delete.html'
    success_url = reverse_lazy('foliarrecipes:supplier_list')

# SupplierMineralProduct Views
class SupplierMineralProductListView(LoginRequiredMixin, ListView):
    model = SupplierMineralProduct
    context_object_name = 'supplier_mineral_products'
    template_name = 'foliarrecipes/suppliermineralproduct_list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.groups.exists():
            return queryset.filter(supplier__group__in=self.request.user.groups.all())
        return queryset.filter(supplier__group__isnull=True)

class SupplierMineralProductDetailView(LoginRequiredMixin, DetailView):
    model = SupplierMineralProduct
    context_object_name = 'supplier_mineral_product'
    template_name = 'foliarrecipes/suppliermineralproduct_detail.html'

class SupplierMineralProductCreateView(LoginRequiredMixin, CreateView):
    model = SupplierMineralProduct
    template_name = 'foliarrecipes/suppliermineralproduct_form.html'
    fields = ['supplier', 'mineral_raw', 'product_code', 'package_size', 
              'package_unit', 'price', 'minimum_order', 'url', 'notes']
    success_url = reverse_lazy('foliarrecipes:suppliermineralproduct_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter suppliers by user's group
        if self.request.user.groups.exists():
            form.fields['supplier'].queryset = Supplier.objects.filter(group__in=self.request.user.groups.all())
        else:
            form.fields['supplier'].queryset = Supplier.objects.filter(group__isnull=True)
        # Filter mineral_raw by user's group
        if self.request.user.groups.exists():
            form.fields['mineral_raw'].queryset = MineralRaw.objects.filter(group__in=self.request.user.groups.all())
        else:
            form.fields['mineral_raw'].queryset = MineralRaw.objects.filter(group__isnull=True)
        return form

    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a supplier mineral product.')
            return self.form_invalid(form)
        form.instance.group = group
        messages.success(self.request, 'Supplier mineral product created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'suppliermineralproducts'
        context['page_action'] = 'form'
        context['groups'] = Group.objects.all()
        return context

class SupplierMineralProductUpdateView(LoginRequiredMixin, UpdateView):
    model = SupplierMineralProduct
    template_name = 'foliarrecipes/suppliermineralproduct_form.html'
    fields = ['supplier', 'mineral_raw', 'product_code', 'package_size', 
              'package_unit', 'price', 'minimum_order', 'url', 'notes']
    success_url = reverse_lazy('foliarrecipes:suppliermineralproduct_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter suppliers by user's group
        if self.request.user.groups.exists():
            form.fields['supplier'].queryset = Supplier.objects.filter(group__in=self.request.user.groups.all())
        else:
            form.fields['supplier'].queryset = Supplier.objects.filter(group__isnull=True)
        # Filter mineral_raw by user's group
        if self.request.user.groups.exists():
            form.fields['mineral_raw'].queryset = MineralRaw.objects.filter(group__in=self.request.user.groups.all())
        else:
            form.fields['mineral_raw'].queryset = MineralRaw.objects.filter(group__isnull=True)
        return form

    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a supplier mineral product.')
            return self.form_invalid(form)
        form.instance.group = group
        messages.success(self.request, 'Supplier mineral product created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'suppliermineralproducts'
        context['page_action'] = 'form'
        context['groups'] = Group.objects.all()
        return context

class SupplierMineralProductDeleteView(LoginRequiredMixin, DeleteView):
    model = SupplierMineralProduct
    template_name = 'foliarrecipes/suppliermineralproduct_confirm_delete.html'
    success_url = reverse_lazy('foliarrecipes:suppliermineralproduct_list')

# SupplierChelatingProduct Views
class SupplierChelatingProductListView(LoginRequiredMixin, ListView):
    model = SupplierChelatingProduct
    context_object_name = 'supplier_chelating_products'
    template_name = 'foliarrecipes/supplierchelatingproduct_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.groups.exists():
            return queryset.filter(Q(supplier__group__in=self.request.user.groups.all()) | Q(supplier__group__isnull=True))
        return queryset.filter(supplier__group__isnull=True)

class SupplierChelatingProductDetailView(LoginRequiredMixin, DetailView):
    model = SupplierChelatingProduct
    context_object_name = 'supplier_chelating_product'
    template_name = 'foliarrecipes/supplierchelatingproduct_detail.html'

class SupplierChelatingProductCreateView(LoginRequiredMixin, CreateView):
    model = SupplierChelatingProduct
    template_name = 'foliarrecipes/supplierchelatingproduct_form.html'
    fields = ['supplier', 'chelating_agent', 'product_code', 'package_size',
             'package_unit', 'price', 'minimum_order', 'url', 'notes']
    success_url = reverse_lazy('foliarrecipes:supplierchelatingproduct_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.groups.exists():
            form.fields['supplier'].queryset = Supplier.objects.filter(
                Q(group__in=self.request.user.groups.all()) | Q(group__isnull=True)
            )
        else:
            form.fields['supplier'].queryset = Supplier.objects.filter(group__isnull=True)
        return form

    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a supplier chelating product.')
            return self.form_invalid(form)
        form.instance.group = group
        messages.success(self.request, 'Supplier chelating product created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'supplierchelatingproducts'
        context['page_action'] = 'form'
        context['groups'] = Group.objects.all()
        return context

class SupplierChelatingProductUpdateView(LoginRequiredMixin, UpdateView):
    model = SupplierChelatingProduct
    template_name = 'foliarrecipes/supplierchelatingproduct_form.html'
    fields = ['supplier', 'chelating_agent', 'product_code', 'package_size',
             'package_unit', 'price', 'minimum_order', 'url', 'notes']
    success_url = reverse_lazy('foliarrecipes:supplierchelatingproduct_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.groups.exists():
            form.fields['supplier'].queryset = Supplier.objects.filter(
                Q(group__in=self.request.user.groups.all()) | Q(group__isnull=True)
            )
        else:
            form.fields['supplier'].queryset = Supplier.objects.filter(group__isnull=True)
        return form

    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a supplier chelating product.')
            return self.form_invalid(form)
        form.instance.group = group
        messages.success(self.request, 'Supplier chelating product created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'supplierchelatingproducts'
        context['page_action'] = 'form'
        context['groups'] = Group.objects.all()
        return context

class SupplierChelatingProductDeleteView(LoginRequiredMixin, DeleteView):
    model = SupplierChelatingProduct
    template_name = 'foliarrecipes/supplierchelatingproduct_confirm_delete.html'
    success_url = reverse_lazy('foliarrecipes:supplierchelatingproduct_list')

# ChelatingAgent Views
class ChelatingAgentListView(LoginRequiredMixin, ListView):
    model = ChelatingAgent
    context_object_name = 'chelating_agents'
    template_name = 'foliarrecipes/chelatingagent_list.html'
    
    def get_queryset(self):
        # Filter by user's group if group is set
        queryset = super().get_queryset()
        if self.request.user.groups.exists():
            return queryset.filter(group__in=self.request.user.groups.all())
        return queryset.filter(group__isnull=True)

class ChelatingAgentDetailView(LoginRequiredMixin, DetailView):
    model = ChelatingAgent
    context_object_name = 'chelating_agent'
    template_name = 'foliarrecipes/chelatingagent_detail.html'

class ChelatingAgentCreateView(LoginRequiredMixin, CreateView):
    model = ChelatingAgent
    template_name = 'foliarrecipes/chelatingagent_form.html'
    fields = ['name', 'form', 'chemical_formula', 'optimal_ph_range', 
              'solubility', 'stability_notes', 'notes']
    success_url = reverse_lazy('foliarrecipes:chelatingagent_list')

    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a chelating agent.')
            return self.form_invalid(form)
        form.instance.group = group
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'chelatingagent'
        context['page_action'] = 'form'
        context['groups'] = Group.objects.all()
        return context

class ChelatingAgentUpdateView(LoginRequiredMixin, UpdateView):
    model = ChelatingAgent
    template_name = 'foliarrecipes/chelatingagent_form.html'
    fields = ['name', 'form', 'chemical_formula', 'optimal_ph_range', 
              'solubility', 'stability_notes', 'notes']
    success_url = reverse_lazy('foliarrecipes:chelatingagent_list')

    def form_valid(self, form):
        # Set the group if user belongs to one 
        if self.request.user.groups.exists():
            form.instance.group = self.request.user.groups.first()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'chelatingagent'
        context['page_action'] = 'form'
        context['groups'] = Group.objects.all()
        return context

class ChelatingAgentDeleteView(LoginRequiredMixin, DeleteView):
    model = ChelatingAgent
    template_name = 'foliarrecipes/chelatingagent_confirm_delete.html'
    success_url = reverse_lazy('foliarrecipes:chelatingagent_list')

# ChelatedMineral Views
class ChelatedMineralListView(LoginRequiredMixin, ListView):
    model = ChelatedMineral
    context_object_name = 'chelated_minerals'
    template_name = 'foliarrecipes/chelatedmineral_list.html'

    def get_queryset(self):
        return ChelatedMineral.objects.filter(group__in=self.request.user.groups.all())

class ChelatedMineralDetailView(LoginRequiredMixin, DetailView):
    model = ChelatedMineral
    context_object_name = 'chelated_mineral'
    template_name = 'foliarrecipes/chelatedmineral_detail.html'

class ChelatedMineralCreateView(LoginRequiredMixin, CreateView):
    model = ChelatedMineral
    template_name = 'foliarrecipes/chelatedmineral_form.html'
    fields = ['name', 'mineral_raw', 'mineral_amount', 'water_amount', 
             'ph_target', 'temperature', 'chelating_agent', 'chelating_agent_amount',
             'process', 'notes']
    success_url = reverse_lazy('foliarrecipes:chelatedmineral_list')

    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a chelated mineral.')
            return self.form_invalid(form)
        form.instance.group = group
        messages.success(self.request, 'Chelated mineral created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'chelatedminerals'
        context['page_action'] = 'form'
        context['groups'] = Group.objects.all()
        return context

class ChelatedMineralUpdateView(LoginRequiredMixin, UpdateView):
    model = ChelatedMineral
    template_name = 'foliarrecipes/chelatedmineral_form.html'
    fields = ['name', 'mineral_raw', 'mineral_amount', 'water_amount', 
             'ph_target', 'temperature', 'chelating_agent', 'chelating_agent_amount',
             'process', 'notes']
    success_url = reverse_lazy('foliarrecipes:chelatedmineral_list')

    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a chelated mineral.')
            return self.form_invalid(form)
        form.instance.group = group
        messages.success(self.request, 'Chelated mineral created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'chelatedminerals'
        context['page_action'] = 'form'
        context['groups'] = Group.objects.all()
        return context

class ChelatedMineralDeleteView(LoginRequiredMixin, DeleteView):
    model = ChelatedMineral
    template_name = 'foliarrecipes/chelatedmineral_confirm_delete.html'
    success_url = reverse_lazy('foliarrecipes:chelatedmineral_list')

# RecipeIngredient Views
class RecipeIngredientListView(LoginRequiredMixin, ListView):
    model = RecipeIngredient
    context_object_name = 'recipe_ingredients'
    template_name = 'foliarrecipes/recipeingredient_list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.groups.exists():
            return queryset.filter(group__in=self.request.user.groups.all())
        return queryset.filter(group__isnull=True)

class RecipeIngredientDetailView(LoginRequiredMixin, DetailView):
    model = RecipeIngredient
    context_object_name = 'recipe_ingredient'
    template_name = 'foliarrecipes/recipeingredient_detail.html'

class RecipeIngredientCreateView(LoginRequiredMixin, CreateView):
    model = RecipeIngredient
    template_name = 'foliarrecipes/recipeingredient_form.html'
    fields = ['name', 'amount', 'unit', 'purpose', 'optional', 'order']
    success_url = reverse_lazy('foliarrecipes:recipeingredient_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'recipeingredients'
        context['page_action'] = 'form'
        context['groups'] = Group.objects.all()
        return context
        
    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a recipe ingredient.')
            return self.form_invalid(form)
        
        form.instance.group = group
        return super().form_valid(form)

class RecipeIngredientUpdateView(LoginRequiredMixin, UpdateView):
    model = RecipeIngredient
    template_name = 'foliarrecipes/recipeingredient_form.html'
    fields = ['name', 'amount', 'unit', 'purpose', 'optional', 'order']
    success_url = reverse_lazy('foliarrecipes:recipeingredient_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'foliarrecipes'
        context['page_name'] = 'recipeingredients'
        context['page_action'] = 'form'
        context['groups'] = Group.objects.all()
        return context
        
    def form_valid(self, form):
        group = get_user_group(self.request)
        if not group:
            form.add_error(None, 'You must be a member of at least one group to create a recipe ingredient.')
            return self.form_invalid(form)
        form.instance.group = group
        return super().form_valid(form)

class RecipeIngredientDeleteView(LoginRequiredMixin, DeleteView):
    model = RecipeIngredient
    template_name = 'foliarrecipes/recipeingredient_confirm_delete.html'
    success_url = reverse_lazy('foliarrecipes:recipeingredient_list')
