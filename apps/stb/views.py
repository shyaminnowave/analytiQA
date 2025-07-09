from django.views import generic


class STBView(generic.TemplateView):

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        pass