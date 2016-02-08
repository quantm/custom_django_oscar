from django.conf.urls import *
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from apps.app import shop
from apps.dashboard.catalogue.app import application as catalogue_url
from lib.paypal.payflow.app import application as payflow
from lib.paypal.express.dashboard.app import application as express_dashboard
admin.autodiscover()

urlpatterns = patterns('',
    (r'^checkout/paypal/', include('lib.paypal.express.urls')),
    (r'^dashboard/paypal/payflow/', include(payflow.urls)),
    (r'^dashboard/catalogue/', include(catalogue_url.urls)),
    (r'^dashboard/paypal/express/', include(express_dashboard.urls)),
    (r'^admin/', include(admin.site.urls)),
    (r'', include(shop.urls)),
    (r'^products/', include('apps.products.urls')),
    (r'^collection/', include('apps.collection.urls')),
    (r'^social/', include('apps.social.urls')),
    (r'^api/', include('apps.oscar_api.urls')),
    (r'^bookmark-let/', include('apps.bookmarklet.urls')),
    (r'^networks/', include('apps.networks.urls')),
    (r'^', include('apps.customer.urls')),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
