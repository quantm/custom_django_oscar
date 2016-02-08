from django.conf.urls import *
from apps.networks.views.facebook import *

urlpatterns = patterns('apps.networks.views.facebook',
   url(r'^oauth/', 'check_logged', name='check-logged'),
   url(r'^albums/', 'fb_albums', name='fb_albums'),
   url(r'^album/(?P<album_id>\d+)/', 'fb_open_album', name='fb_open_album'),
   url(r'^photo/(?P<photo_id>\d+)/', 'fb_get_photo_and_save_to_media', name='fb_get_photo_and_save_to_media'),
)

