from django.urls import path
from . import views

app_name = 'minerals'

urlpatterns = [
    # Mineral Nutrient URLs
    path('', views.MineralNutrientListView.as_view(), name='mineral_list'),
    path('mineral/<int:pk>/', views.MineralNutrientDetailView.as_view(), name='mineral_detail'),
    path('mineral/add/', views.MineralNutrientCreateView.as_view(), name='mineral_add'),
    path('mineral/<int:pk>/edit/', views.MineralNutrientUpdateView.as_view(), name='mineral_edit'),
    path('mineral/<int:pk>/delete/', views.MineralNutrientDeleteView.as_view(), name='mineral_delete'),
    
    # Plant Nutrient Requirement URLs
    path('requirements/', views.PlantNutrientRequirementListView.as_view(), name='plant_requirement_list'),
    path('requirement/<int:pk>/', views.PlantNutrientRequirementDetailView.as_view(), name='plant_requirement_detail'),
    path('requirement/add/', views.PlantNutrientRequirementCreateView.as_view(), name='plant_requirement_add'),
    path('requirement/<int:pk>/edit/', views.PlantNutrientRequirementUpdateView.as_view(), name='plant_requirement_edit'),
    path('requirement/<int:pk>/delete/', views.PlantNutrientRequirementDeleteView.as_view(), name='plant_requirement_delete'),
    
    # Nutrient Note URLs
    path('notes/', views.NutrientNoteListView.as_view(), name='nutrient_note_list'),
    path('note/<int:pk>/', views.NutrientNoteDetailView.as_view(), name='nutrient_note_detail'),
    path('note/add/', views.NutrientNoteCreateView.as_view(), name='nutrient_note_add'),
    path('note/<int:pk>/edit/', views.NutrientNoteUpdateView.as_view(), name='nutrient_note_edit'),
    path('note/<int:pk>/delete/', views.NutrientNoteDeleteView.as_view(), name='nutrient_note_delete'),
    
    # Mineral URL URLs
    path('urls/', views.MineralUrlListView.as_view(), name='mineral_url_list'),
    path('url/<int:pk>/', views.MineralUrlDetailView.as_view(), name='mineral_url_detail'),
    path('url/add/', views.MineralUrlCreateView.as_view(), name='mineral_url_add'),
    path('url/<int:pk>/edit/', views.MineralUrlUpdateView.as_view(), name='mineral_url_edit'),
    path('url/<int:pk>/delete/', views.MineralUrlDeleteView.as_view(), name='mineral_url_delete'),
]
