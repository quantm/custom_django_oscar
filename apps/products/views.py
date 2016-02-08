import os, urllib, time, hashlib, cStringIO, string, settings, PIL.Image as Image, json
from settings import MEDIA_ROOT, OSCAR_IMAGE_FOLDER
from datetime import datetime
from .forms import ProductForm

from django.views.generic import ListView
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from oscar.core.utils import slugify
from oscar.apps.catalogue.models import ProductClass
from oscar.apps.customer.mixins import PageTitleMixin
'''from oscar.apps.catalogue.views import ProductListView as CoreProductListView'''

from apps.collection.models import *
from apps.catalogue.models import ProductImage, Product
from apps.common.decorator import *
from apps.social.models import SocialPromote
from core.models import User
from apps.common.functions import save_image_file

def get_or_create_product_class():
    #Product class
    products = ProductClass.objects.all()
    if len(products) > 0:
        product_class = products[0]
    else:
        pro_cls_name = u'Default'
        pro_cls_slug = slugify(pro_cls_name)
        product_class = ProductClass(name=pro_cls_name, slug=pro_cls_slug)
        product_class.save()

    return product_class


@LoginRequired
def save_product(request):
    message = {
        'code': 0,
        'link': {},
        'back_text': _('Add more Products'),
        'message': _("Product hasn't been saved"),
    }

    product_form = ProductForm(request.POST or None)
    if product_form.is_valid():
        try:
            #Get information for Product
            title = request.POST.get('title')
            slug = slugify(title)
            description = request.POST.get('description')
            image_url_from_web = urllib.unquote(request.POST.get('image')).decode('utf8')

            product_class = get_or_create_product_class()

            #Save product object
            product = Product(title=title, slug=slug, description=description, product_class=product_class, user_id=request.user.pk)
            product.save()

            save_image = save_image_file(image_url_from_web, 'product')

            if save_image.get('code') == 1:
                product_image = ProductImage(product=product, original=save_image.get('image_url'), caption=title, display_order=0)
                product_image.save()

            message = {
                'code': 1,
                'object_id': product.id,
                'link': {'url': '/catalogue/%s_%d/' % (slug, product.id), 'text': _('See the product')},
                'back_text': _('Add more Products'),
                'message': _('Product has been saved'),
            }
        except Exception, err:
            pass

    return message


class MyProductView(LoginRequiredMixin, PageTitleMixin, ListView):
    context_object_name = active_tab = "my-products"
    template_name = 'catalogue/products/my_products.html'
    page_title = _('My Recommendations')
    model = SocialPromote

    def get_context_data(self, **kwargs):
        context = super(MyProductView, self).get_context_data(**kwargs)
        my_product_list = SocialPromote.objects.filter(user=self.request.user).order_by('-create_date')
        paginator = Paginator(my_product_list, settings.PRODUCT_ITEM_PER_PAGE)
        page = self.request.GET.get('page')

        try:
            context['my_product_list'] = paginator.page(page)
        except PageNotAnInteger:
            context['my_product_list'] = paginator.page(1)
        except EmptyPage:
            context['my_product_list'] = paginator.page(paginator.num_pages)

        return context

    def get_queryset(self):
        return super(MyProductView, self).get_queryset()

class MyProductViewOtherProfile(LoginRequiredMixin, PageTitleMixin, ListView):
    context_object_name = active_tab = "my-products"
    template_name = 'catalogue/products/my_products_view_profile.html'
    page_title = _('Recommendations')
    model = SocialPromote

    def get_context_data(self, **kwargs):
        context = super(MyProductViewOtherProfile, self).get_context_data(**kwargs)
        user_id = self.kwargs['user_id']
        view_user = User.objects.get(id=user_id)
        context['view_user'] = view_user
        my_product_list = SocialPromote.objects.filter(user=view_user).order_by('-create_date')
        paginator = Paginator(my_product_list, settings.PRODUCT_ITEM_PER_PAGE)
        page = self.request.GET.get('page')

        try:
            context['my_product_list'] = paginator.page(page)
        except PageNotAnInteger:
            context['my_product_list'] = paginator.page(1)
        except EmptyPage:
            context['my_product_list'] = paginator.page(paginator.num_pages)

        return context

    def get_queryset(self):
        return super(MyProductViewOtherProfile, self).get_queryset()

class MyProductAjaxView(LoginRequiredMixin, ListView):
    context_object_name = "my_product_list"
    template_name = 'catalogue/products/ajax_response_my_product.html'
    model = SocialPromote
    paginate_by = settings.PRODUCT_ITEM_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super(MyProductAjaxView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        my_product_list = SocialPromote.objects.filter(user=self.request.user).order_by('-create_date')
        return my_product_list

'''
class ProductListAjaxView(CoreProductListView):

    template_name = 'catalogue/products/ajax_response.html'
    paginate_by = settings.PRODUCT_ITEM_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super(ProductListAjaxView, self).get_context_data(**kwargs)
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
'''

@LoginRequired
def add_this_product(request):
    if request.is_secure():
        host = 'https://%s' % request.get_host()
    else:
        host = 'http://%s' % request.get_host()

    from apps.networks.views import facebook as fb_view
    signed_request = request.GET.get('signed_request')

    message = fb_view.add_this_product(request, signed_request, host)
    return message
