#__author__ = 'tqn'
from django.conf.urls import *
from apps.collection.views.media import *

urlpatterns = patterns('apps.collection.views.media',

   url(r'^add/$', 'add_media', name='modal-add-media'),
   url(r'^list/(?P<type>\w+)/$', CollectionMediaLoad_ListView.as_view(), name='my-list-list-of-type'),

   #Video
   url(r'^video/$', CollectionVideo_ListView.as_view(), name='my-videos'),
   url(r'^video/(?P<pk>\d+)/$', CollectionVideo_DetailView.as_view(), name='video-detail'),

   #View video other profile
   url(r'^video-user-view/(?P<user_id>\d+)/$', CollectionVideoListViewOtherProfile.as_view(), name='my-video-other-profile'),
   url(r'^video-detail-view/(?P<pk>\d+)/$', CollectionVideoOtherProfileDetailView.as_view(), name='video-detail-other-profile'),

   #Image
   url(r'^images/$', CollectionImages_ListView.as_view(), name='my-images'),

   #View Image other profile
   url(r'^images-user-view/(?P<user_id>\d+)/$', CollectionImagesListViewOtherProfile.as_view(), name='my-images-other-profile'),

   url(r'^remove/(?P<pk>\d+)/$', 'remove_media', name='remove-media'),

   url(r'^save/(?P<type>\w+)/$', 'save_media', name='save-media'),

)



