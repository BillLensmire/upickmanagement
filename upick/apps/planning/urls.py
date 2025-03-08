from django.urls import path
from . import views

app_name = 'planning'

urlpatterns = [
    # Garden Plan URLs
    #path('garden-plans/', views.GardenPlanListView.as_view(), name='garden_plan_list'),
    #path('garden-plans/create/', views.GardenPlanCreateView.as_view(), name='garden_plan_create'),
    #path('garden-plans/<int:pk>/', views.GardenPlanDetailView.as_view(), name='garden_plan_detail'),
    #path('garden-plans/<int:pk>/edit/', views.GardenPlanUpdateView.as_view(), name='garden_plan_edit'),
    #path('garden-plans/<int:pk>/delete/', views.GardenPlanDeleteView.as_view(), name='garden_plan_delete'),
]