#__author__ = 'tqn'
from django.conf.urls import *
from django.contrib.auth.decorators import login_required
from .views import *


urlpatterns = patterns('apps.products.views',
   url(r'^my-products/$', MyProductView.as_view(), name='my-products'),
   url(r'^my-product-of-page/(?P<page>\d+)/$', MyProductAjaxView.as_view(), name='my-product-of-page'),
   #url(r'^view-product-of-page/(?P<page>\d+)/', ProductListAjaxView.as_view(), name='view-product-of-page'),
   url(r'^add-this/', 'add_this_product', name='add-this-product'),
   url(r'^my-products/(?P<user_id>\d+)/$', MyProductViewOtherProfile.as_view(), name='my-product-other-profile'),
)

