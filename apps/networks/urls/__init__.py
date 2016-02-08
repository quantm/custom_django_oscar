from django.conf.urls import *

urlpatterns = patterns('',
   (r'^fb/', include('apps.networks.urls.facebook')),
   (r'^instagram/', include('apps.networks.urls.instagram')),
   (r'^pinterest/', include('apps.networks.urls.pinterest')),
   (r'^youtube/', include('apps.networks.urls.youtube')),
   (r'^flickr/', include('apps.networks.urls.flickr')),
   (r'^photobucket/', include('apps.networks.urls.photobucket')),
   (r'^vine/', include('apps.networks.urls.vine')),
)