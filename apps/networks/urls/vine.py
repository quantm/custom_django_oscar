from django.conf.urls import *
from apps.networks.views.vine import *

urlpatterns = patterns('apps.networks.views.vine',
    url(r'^search/$', SearchVideos.as_view(), name='vine-search-videos'),
)