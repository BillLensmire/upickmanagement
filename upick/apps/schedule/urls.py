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
    
    # Todo Task URLs
    path('todo-tasks/', views.TodoTaskListView.as_view(), name='todo_task_list'),
    path('todo-tasks/create/', views.TodoTaskCreateView.as_view(), name='todo_task_create'),
    path('todo-tasks/<int:pk>/', views.TodoTaskDetailView.as_view(), name='todo_task_detail'),
    path('todo-tasks/<int:pk>/edit/', views.TodoTaskUpdateView.as_view(), name='todo_task_update'),
    path('todo-tasks/<int:pk>/delete/', views.TodoTaskDeleteView.as_view(), name='todo_task_delete'),
    path('todo-tasks/<int:pk>/markcomplete/', views.TodoTaskMarkComplete, name='todo_task_mark_complete'),
    
    # Todo List URLs
    path('todo-lists/', views.TodoListListView.as_view(), name='todo_list_list'),
    path('todo-lists/create/', views.TodoListCreateView.as_view(), name='todo_list_create'),
    path('todo-lists/<int:pk>/', views.TodoListDetailView.as_view(), name='todo_list_detail'),
    path('todo-lists/<int:pk>/edit/', views.TodoListUpdateView.as_view(), name='todo_list_update'),
    path('todo-lists/<int:pk>/delete/', views.TodoListDeleteView.as_view(), name='todo_list_delete'),
    
    # Planting Schedule URLs
    path('', views.schedule_list, name='list'),
    path('<int:pk>/viewplanningschedule/', views.ViewPlantingScheduleView.as_view(), name='view_planning_schedule'),
    path('create/', views.ScheduleCreateView.as_view(), name='create'),
    path('<int:schedule_id>/', views.ScheduleDetailView.as_view(), name='detail'),
    path('<int:schedule_id>/edit/', views.ScheduleUpdateView.as_view(), name='edit'),
    path('<int:schedule_id>/duplicate/', views.schedule_duplicate, name='duplicate'),
    path('<int:pk>/delete/', views.ScheduleDeleteView.as_view(), name='delete'),
    path('planting-schedule/<int:schedule_id>/update-planting-date/', views.update_planting_date, name='update_planting_date'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/events/', views.get_calendar_events, name='calendar_events'),
    path('calendar/export/', views.export_calendar_pdf, name='export_calendar'),
]