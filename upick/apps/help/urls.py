from django.urls import path
from .views import MarkdownHelpView, NutrientNotesHelpView

app_name = 'help'

urlpatterns = [
    path('markdown-latex/', MarkdownHelpView.as_view(), name='markdown_latex_help'),
    path('nutrient-notes/', NutrientNotesHelpView.as_view(), name='nutrient_notes_help'),
]
