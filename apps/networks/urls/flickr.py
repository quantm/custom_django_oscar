from django.conf.urls import *
from apps.networks.views.flickr import *

urlpatterns = patterns('apps.networks.views.flickr',
   url(r'^search/', SearchImages.as_view(), name='flickr-search-image'),
   url(r'^test/', 'search_images_testing', name='search-images-testing'),
)

