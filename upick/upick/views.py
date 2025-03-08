from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_app'] = 'produce_planner'
        context['page_name'] = 'home'
        context['page_action'] = 'view'
        return context
