from django.urls import path
from . import views

app_name = 'beneficials'

urlpatterns = [
    path('', views.BeneficialListView.as_view(), name='list'),
    path('create/', views.BeneficialCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.BeneficialUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.BeneficialDeleteView.as_view(), name='delete'),
]
