from django.conf.urls import *

urlpatterns = patterns('',
   (r'', include('apps.collection.urls.collection')),
   (r'^my-list/', include('apps.collection.urls.list')),
   (r'^media/', include('apps.collection.urls.medias')),
)