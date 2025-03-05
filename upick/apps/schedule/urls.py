from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    # Garden Bed URLs
    path('garden-beds/', views.GardenBedListView.as_view(), name='garden_bed_list'),
    path('garden-beds/create/', views.GardenBedCreateView.as_view(), name='garden_bed_create'),
    path('garden-beds/<int:pk>/', views.GardenBedDetailView.as_view(), name='garden_bed_detail'),
    path('garden-beds/<int:pk>/edit/', views.GardenBedUpdateView.as_view(), name='garden_bed_edit'),
    path('garden-beds/<int:pk>/delete/', views.GardenBedDeleteView.as_view(), name='garden_bed_delete'),
    
    path('', views.schedule_list, name='list'),
    path('create/', views.schedule_create, name='create'),
    path('<int:schedule_id>/', views.schedule_detail, name='detail'),
    path('<int:schedule_id>/edit/', views.schedule_edit, name='edit'),
    path('<int:schedule_id>/duplicate/', views.schedule_duplicate, name='duplicate'),
    path('planting-schedule/<int:schedule_id>/update-planting-date/', 
         views.update_planting_date, 
         name='update_planting_date'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/events/', views.get_calendar_events, name='calendar_events'),
    path('calendar/export/', views.export_calendar_pdf, name='export_calendar'),
]