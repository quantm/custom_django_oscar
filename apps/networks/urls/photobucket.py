from django.conf.urls import *
from apps.networks.views.photobucket import *

urlpatterns = patterns('apps.networks.views.photobucket',
   url(r'^search/', SearchImages.as_view(), name='flickr-search-image'),
)

