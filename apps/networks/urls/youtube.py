
from django.conf.urls import *
from apps.networks.views.youtube import *

urlpatterns = patterns('apps.networks.views.youtube',
   url(r'^search/$', SearchVideos.as_view(), name='search-videos'),
   url(r'^upload-widget/$', 'youtube_upload_widget', name='youtube_upload_widget'),
)





