from django.conf.urls import *
from apps.networks.views.pinterest import *

urlpatterns = patterns('apps.networks.views.pinterest',
    url(r'^search/$', SearchImages.as_view(), name='pinterest-search-images'),
)