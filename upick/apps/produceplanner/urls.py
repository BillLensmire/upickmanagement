from django.urls import path
from . import views
from apps.produceplanner.models import ProducePlanOverview
app_name = 'produceplanner'

urlpatterns = [
    path('', views.ProducePlanOverviewListView.as_view(), name='overview_list'),
    path('create/', views.ProducePlanOverviewCreateView.as_view(), name='overview_create'),
    path('<int:pk>/', views.ProducePlanOverviewDetailView.as_view(), name='overview_detail'),
    path('<int:pk>/edit/', views.ProducePlanOverviewUpdateView.as_view(), name='overview_update'),
    path('report/<int:overview_id>/', views.produce_availability_report, name='produce_availability_report'),
    path('plan/<int:plan_id>/update-planting-date/', views.update_planting_date, name='update_planting_date'),
    
    # ProducePlan URLs
    path('<int:overview_id>/produce/create/', views.ProducePlanCreateView.as_view(), name='produceplan_create'),
    path('produce/<int:pk>/update/', views.ProducePlanUpdateView.as_view(), name='produceplan_update'),
    path('produce/<int:pk>/delete/', views.ProducePlanDeleteView.as_view(), name='produceplan_delete'),
]