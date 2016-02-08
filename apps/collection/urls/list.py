#__author__ = 'tqn'
from django.conf.urls import *
from apps.collection.views.list import *
urlpatterns = patterns('apps.collection.views.list',
   #My list
   url(r'^$', MyListProfile.as_view(), name='my-list-profile'),
   url(r'^(?P<pk>\d+)/$', MyListDetail.as_view(), name='my-list-detail'),
   url(r'^(?P<pk>\d+)/delete/$', MyListDelete.as_view(), name='my-list-delete'),
   url(r'^delete/(?P<pk>\d+)/$', 'my_list_delete', name='delete-my-list'),

   url(r'^remove/(?P<list_pk>\d+)/(?P<item_id>\d+)/$', 'my_list_remove_item', name='my-list-remove-item'),

   #View My List of other user
   url(r'^my-list-user-view/(?P<user_id>\d+)/$', MyListOtherProfile.as_view(), name='my-list-other-profile'),
   url(r'^my-list-detail-view/(?P<pk>\d+)/$', MyListOtherProfileDetail.as_view(), name='my-list-detail-other-profile'),

)



