from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from oscar.apps.basket.views import BasketView
from django.http import HttpResponseRedirect, HttpResponse
#from apps.shipping.repository import Repository
from oscar.apps.basket.views import BasketAddView as CoreBasketAddView


class BasketAddView(CoreBasketAddView):
    def form_valid(self, form):

        if self.request.is_ajax():
            self.request.basket.add_product(
            form.instance, form.cleaned_data['quantity'],
            form.cleaned_options())
            return HttpResponse(render_to_string('basket/ajax_reponse.html', {'basket': self.request.basket}))
        return super(BasketAddView, self).form_valid(form)

    def form_invalid(self, form):

        if self.request.is_ajax():
            return HttpResponse('error')

        return HttpResponseRedirect(
            self.request.META.get('HTTP_REFERER', reverse('basket:summary')))


class BasketView(BasketView):
    def get_context_data(self, **kwargs):
        context = super(BasketView, self).get_context_data(**kwargs)
        context['order_preview'] = True
        return context