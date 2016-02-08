from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from django.db.models import get_model
from django.contrib.sites.models import Site
from oscar.core.loading import get_class
from oscar.apps.catalogue.signals import product_viewed
from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
import settings
from django.utils.translation import ugettext as _

from apps.social.models import SocialPromote
Product = get_model('catalogue', 'product')
ProductReview = get_model('reviews', 'ProductReview')
Category = get_model('catalogue', 'category')
ProductAlert = get_model('customer', 'ProductAlert')
ProductAlertForm = get_class('customer.forms', 'ProductAlertForm')

'''
class ProductListView(CoreProductListView):
    paginate_by = settings.PRODUCT_ITEM_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        q = self.get_search_query()
        qs = Product.browsable.base_queryset()
        if q:
            # Send signal to record the view of this product
            self.search_signal.send(sender=self, query=q, user=self.request.user)
            return qs.filter(title__icontains=q)
        else:
            return qs.filter(stockrecords__isnull=False).distinct()


class ProductDetailView(CoreProductDetailView):
    context_object_name = 'product'
    model = Product
    view_signal = product_viewed
    template_folder = "catalogue"

    def get(self, request, **kwargs):
        """
        Ensures that the correct URL is used before rendering a response
        """
        self.object = product = self.get_object()

        promote_id = 0
        try:
            promote_id= self.request.GET['p']
        except Exception, err:
            pass

        if promote_id > 0:
            promote_data = SocialPromote.objects.filter(pk=promote_id)
            if promote_data:
                promote_data = promote_data[0]
                if product.id != promote_data.product.id:
                    return HttpResponsePermanentRedirect(promote_data.product.get_absolute_url() + '?p=' + str(promote_data.id))
            else:
                return HttpResponse('<h1>' + _('Page not found') + '</h1>', status=404)

        if product.is_variant:
            return HttpResponsePermanentRedirect(
                product.parent.get_absolute_url())

        correct_path = product.get_absolute_url()
        if correct_path != request.path:
            return HttpResponsePermanentRedirect(correct_path)

        response = super(ProductDetailView, self).get(request, **kwargs)
        self.send_signal(request, response, product)
        return response

    def get_object(self, queryset=None):
        # Check if self.object is already set to prevent unnecessary DB calls
        if hasattr(self, 'object'):
            return self.object
        else:
            return super(ProductDetailView, self).get_object(queryset)

    def get_context_data(self, **kwargs):
        ctx = super(ProductDetailView, self).get_context_data(**kwargs)
        ctx['reviews'] = self.get_reviews()
        ctx['alert_form'] = self.get_alert_form()
        ctx['has_active_alert'] = self.get_alert_status()
        promote_id = 0
        try:
            promote_id= self.request.GET['p']
        except Exception, err:
            pass

        if promote_id > 0:
            promote_data = SocialPromote.objects.filter(pk=promote_id)
            if promote_data:
                ctx['promote_data'] = promote_data[0]
                if ctx['product'].id != ctx['promote_data'].product.id:
                    return redirect(ctx['promote_data'].product.get_absolute_url())
        return ctx

    def get_alert_status(self):
        # Check if this user already have an alert for this product
        has_alert = False
        if self.request.user.is_authenticated():
            alerts = ProductAlert.objects.filter(
                product=self.object, user=self.request.user,
                status=ProductAlert.ACTIVE)
            has_alert = alerts.count() > 0
        return has_alert

    def get_alert_form(self):
        return ProductAlertForm(
            user=self.request.user, product=self.object)

    def get_reviews(self):
        return self.object.reviews.filter(status=ProductReview.APPROVED)

    def send_signal(self, request, response, product):
        self.view_signal.send(
            sender=self, product=product, user=request.user, request=request,
            response=response)

    def get_template_names(self):
        promote_id = 0
        try:
            promote_id= self.request.GET['p']
        except Exception, err:
            pass

        if promote_id > 0:
            return '%s/detail_new.html' % (self.template_folder)

        return [
            '%s/detail-for-upc-%s.html' % (
                self.template_folder, self.object.upc),
            '%s/detail-for-class-%s.html' % (
                self.template_folder, self.object.get_product_class().slug),
            '%s/detail.html' % (self.template_folder)]
    '''