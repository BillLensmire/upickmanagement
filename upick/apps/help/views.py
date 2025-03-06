from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils.html import format_html
from django.urls import reverse


class MarkdownHelpView(TemplateView):
    """View to display help information about Markdown and LaTeX syntax."""
    template_name = 'help/markdown_latex_help.html'


class MarkdownHelpNotesView(TemplateView):
    """View to display help information about Markdown and LaTeX syntax for nutrient notes."""
    template_name = 'help/markdown_latex_notes.html'


class NutrientNotesHelpView(TemplateView):
    """View to display help information about nutrient notes."""
    template_name = 'help/nutrient_notes_help.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        help_url = reverse('help:markdown_latex_help')
        context['notes_help_text'] = format_html('Enter your notes here. <a href="{}" target="_blank">Learn more about formatting</a>', help_url)
        return context
