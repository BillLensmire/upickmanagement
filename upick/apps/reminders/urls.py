from django.urls import path
from . import views

app_name = 'reminders'

urlpatterns = [
    path('', views.reminder_list, name='reminder_list'),
    path('completed/', views.reminder_list_completed, name='reminder_list_completed'),
    path('create/', views.reminder_create, name='reminder_create'),
    path('<int:pk>/', views.reminder_detail, name='reminder_detail'),
    path('<int:pk>/edit/', views.reminder_edit, name='reminder_edit'),
    path('<int:pk>/toggle-complete/', views.reminder_toggle_complete, name='reminder_toggle_complete'),
    path('<int:pk>/duplicate/', views.reminder_duplicate, name='reminder_duplicate'),
]
