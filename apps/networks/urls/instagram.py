from django.conf.urls import *
from apps.networks.views.instagram import *

urlpatterns = patterns('apps.networks.views.instagram',
    url(r'^search/$', SearchImages.as_view(), name='instagram-search-images'),
)


