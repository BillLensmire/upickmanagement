from django.urls import path
from . import views

app_name = 'covercrops'

urlpatterns = [
    # Cover Crop Mix URLs
    path('', views.CoverCropMixListView.as_view(), name='mix_list'),
    path('mix/<int:pk>/', views.CoverCropMixDetailView.as_view(), name='mix_detail'),
    path('mix/create/', views.CoverCropMixCreateView.as_view(), name='mix_create'),
    path('mix/<int:pk>/edit/', views.CoverCropMixUpdateView.as_view(), name='mix_update'),
    path('mix/<int:pk>/delete/', views.CoverCropMixDeleteView.as_view(), name='mix_delete'),
    
    # Cover Crop Plan URLs
    path('plan/', views.CoverCropPlanListView.as_view(), name='plan_list'),
    path('plan/<int:pk>/', views.CoverCropPlanDetailView.as_view(), name='plan_detail'),
    path('plan/create/', views.CoverCropPlanCreateView.as_view(), name='plan_create'),
    path('plan/<int:pk>/edit/', views.CoverCropPlanUpdateView.as_view(), name='plan_update'),
    path('plan/<int:pk>/delete/', views.CoverCropPlanDeleteView.as_view(), name='plan_delete'),
]
