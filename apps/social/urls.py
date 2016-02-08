#__author__ = 'Administrator'
from django.conf.urls import *
from .views import *
from apps.social.views import MyEventListView
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('apps.social.views',
   url(r'^getuser/$', 'get_user', name='get_user'),
   url(r'^gethashtag/$', 'get_hashtag', name='get_hashtag'),
   url(r'^hashtag/$', HashtagList.as_view(), name='HashtagList'),
   url(r'^hashtag/popular/$', TopHashTag.as_view(), name='TopHashTag'),
   url(r'^hashtag/(?P<hashtag>[a-zA-Z|0-9]+)/$', ViewConnectedHashtag.as_view(), name='ViewConnectedHashtag'),
   url(r'^my-friends/$', MyFriendList.as_view(), name="my-friends"),
   url(r'^my-friends/(?P<user_id>\d+)/$', FriendListOtherProfile.as_view(), name="view-friends-other-profile"),
   url(r'^friendship/request/$', request_friend),
   url(r'^save-promote/$', save_promote),
   url(r'^check-user-ready-promote-this-product/$', check_user_ready_promote_this_product),
   url(r'^my-event/$', MyEventListView.as_view(), name='my-events'),
   url(r'^my-event/create/(?P<new>\d+)/$', 'my_event_create_update', name='create-events'),
   url(r'^my-event/update/(?P<event_id>\d+)/$', 'my_event_create_update', name='update-events'),
   url(r'^my-event/user/$', 'my_event_user', name='my_event_user'),
   url(r'^my-event/(?P<event_id>\d+)/$', MyEventListDetail.as_view(), name='detail-events'),
   url(r'^my-event/save/$', 'save_event', name='save_event'),
   url(r'^my-event/delete/(?P<event_id>\d+)/$', 'delete_event_view', name='delete_event'),
   url(r'^my-event/delete/one/$', 'delete_event', name='delete_event_post'),
   url(r'^friend-event/(?P<user_id>\d+)/$', MyEventListOtherProfileView.as_view(), name='my-events-other-profile'),
   url(r'^my-wall/$', MyWall.as_view(), name='my-wall'),
   url(r'^friend-wall/(?P<user_friend_id>\d+)/$', MyWallOtherProfile.as_view(), name='my-wall-other-profile'),
   url(r'^my-wall/message/$', MyWallMessage.as_view(), name='my-wall-message'),
   url(r'^my-wall/post/detail/(?P<post_id>\d+)/$', MyWallConversationDetails.as_view(), name='my-wall-post-detail'),
   url(r'^my-wall/save/$', 'my_wall_save', name='my_wall_save'),
   url(r'^my-wall/delete/$', 'delete_my_wall_message', name='delete_my_wall_message'),
)
