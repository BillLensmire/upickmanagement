from django.urls import path
from . import views

app_name = 'produceplanner'

urlpatterns = [
    path('', views.ProducePlanOverviewListView.as_view(), name='overview_list'),
    path('create/', views.ProducePlanOverviewCreateView.as_view(), name='overview_create'),
    path('<int:pk>/', views.ProducePlanOverviewDetailView.as_view(), name='overview_detail'),
    path('<int:pk>/edit/', views.ProducePlanOverviewUpdateView.as_view(), name='overview_update'),
    path('report/<int:overview_id>/', views.produce_availability_report, name='produce_availability_report'),
    path('plan/<int:plan_id>/update-planting-date/', views.update_planting_date, name='update_planting_date'),
    path('<int:overview_id>/add-produce/', views.add_produce, name='add_produce'),
    path('plan/<int:plan_id>/delete/', views.delete_produce, name='delete_produce'),
]