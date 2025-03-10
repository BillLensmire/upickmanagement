from django.urls import path
from . import views
from apps.produceplanner.views import get_varieties
from .views import SearchMaturityView

app_name = 'plants'

urlpatterns = [
    # Plant URLs
    path('', views.PlantListView.as_view(), name='list'),
    path('add/', views.PlantCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PlantDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PlantUpdateView.as_view(), name='edit'),
    path('search/', views.PlantSearchView.as_view(), name='search'),
    path('<int:pk>/delete/', views.PlantDeleteView.as_view(), name='delete'),
    
    # Variety URLs
    path('varieties/', views.VarietyListView.as_view(), name='variety_list'),
    path('varieties/add/', views.VarietyCreateView.as_view(), name='variety_create'),
    path('<int:plant_pk>/varieties/add/', views.PlantVarietyCreateView.as_view(), name='plant_variety_create'),
    path('varieties/<int:pk>/', views.VarietyDetailView.as_view(), name='variety_detail'),
    path('varieties/<int:pk>/edit/', views.VarietyUpdateView.as_view(), name='variety_edit'),
    path('varieties/search/', views.VarietySearchView.as_view(), name='variety_search'),
    path('varieties/<int:pk>/delete/', views.VarietyDeleteView.as_view(), name='variety_delete'),
    path('get-varieties/<int:pk>/', get_varieties, name='get_varieties'),
    path('varieties/<int:pk>/search_maturity/', SearchMaturityView.as_view(), name='search_maturity'),
]