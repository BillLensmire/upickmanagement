from django.urls import path
from . import views

app_name = 'foliarrecipes'

urlpatterns = [
    # MineralRaw URLs
    path('mineralraw/', views.MineralRawListView.as_view(), name='mineralraw_list'),
    path('mineralraw/add/', views.MineralRawCreateView.as_view(), name='mineralraw_add'),
    path('mineralraw/<int:pk>/', views.MineralRawDetailView.as_view(), name='mineralraw_detail'),
    path('mineralraw/<int:pk>/edit/', views.MineralRawUpdateView.as_view(), name='mineralraw_edit'),
    path('mineralraw/<int:pk>/delete/', views.MineralRawDeleteView.as_view(), name='mineralraw_delete'),

    # Supplier URLs
    path('supplier/', views.SupplierListView.as_view(), name='supplier_list'),
    path('supplier/add/', views.SupplierCreateView.as_view(), name='supplier_add'),
    path('supplier/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('supplier/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('supplier/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),

    # SupplierMineralProduct URLs
    path('suppliermineralproduct/', views.SupplierMineralProductListView.as_view(), name='suppliermineralproduct_list'),
    path('suppliermineralproduct/add/', views.SupplierMineralProductCreateView.as_view(), name='suppliermineralproduct_add'),
    path('suppliermineralproduct/<int:pk>/', views.SupplierMineralProductDetailView.as_view(), name='suppliermineralproduct_detail'),
    path('suppliermineralproduct/<int:pk>/edit/', views.SupplierMineralProductUpdateView.as_view(), name='suppliermineralproduct_edit'),
    path('suppliermineralproduct/<int:pk>/delete/', views.SupplierMineralProductDeleteView.as_view(), name='suppliermineralproduct_delete'),

    # SupplierChelatingProduct URLs
    path('supplierchelatingproduct/', views.SupplierChelatingProductListView.as_view(), name='supplierchelatingproduct_list'),
    path('supplierchelatingproduct/add/', views.SupplierChelatingProductCreateView.as_view(), name='supplierchelatingproduct_add'),
    path('supplierchelatingproduct/<int:pk>/', views.SupplierChelatingProductDetailView.as_view(), name='supplierchelatingproduct_detail'),
    path('supplierchelatingproduct/<int:pk>/edit/', views.SupplierChelatingProductUpdateView.as_view(), name='supplierchelatingproduct_edit'),
    path('supplierchelatingproduct/<int:pk>/delete/', views.SupplierChelatingProductDeleteView.as_view(), name='supplierchelatingproduct_delete'),

    # ChelatedMineral URLs
    path('chelatedmineral/', views.ChelatedMineralListView.as_view(), name='chelatedmineral_list'),
    path('chelatedmineral/add/', views.ChelatedMineralCreateView.as_view(), name='chelatedmineral_add'),
    path('chelatedmineral/<int:pk>/', views.ChelatedMineralDetailView.as_view(), name='chelatedmineral_detail'),
    path('chelatedmineral/<int:pk>/edit/', views.ChelatedMineralUpdateView.as_view(), name='chelatedmineral_edit'),
    path('chelatedmineral/<int:pk>/delete/', views.ChelatedMineralDeleteView.as_view(), name='chelatedmineral_delete'),

    # ChelatingAgent URLs
    path('chelatingagent/', views.ChelatingAgentListView.as_view(), name='chelatingagent_list'),
    path('chelatingagent/add/', views.ChelatingAgentCreateView.as_view(), name='chelatingagent_add'),
    path('chelatingagent/<int:pk>/', views.ChelatingAgentDetailView.as_view(), name='chelatingagent_detail'),
    path('chelatingagent/<int:pk>/edit/', views.ChelatingAgentUpdateView.as_view(), name='chelatingagent_edit'),
    path('chelatingagent/<int:pk>/delete/', views.ChelatingAgentDeleteView.as_view(), name='chelatingagent_delete'),

    # RecipeIngredient URLs
    path('recipeingredient/', views.RecipeIngredientListView.as_view(), name='recipeingredient_list'),
    path('recipeingredient/add/', views.RecipeIngredientCreateView.as_view(), name='recipeingredient_add'),
    path('recipeingredient/<int:pk>/', views.RecipeIngredientDetailView.as_view(), name='recipeingredient_detail'),
    path('recipeingredient/<int:pk>/edit/', views.RecipeIngredientUpdateView.as_view(), name='recipeingredient_edit'),
    path('recipeingredient/<int:pk>/delete/', views.RecipeIngredientDeleteView.as_view(), name='recipeingredient_delete'),
]
