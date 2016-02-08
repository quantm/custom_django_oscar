from django.conf.urls.defaults import *
from rest_framework.urlpatterns import format_suffix_patterns
#from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = patterns('oscar_api.views',
    url(r'^$', api_root),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^products/$', ProductList.as_view(), name='api-product-list'),
    url(r'^products/(?P<pk>\d+)/$', ProductDetail.as_view(), name='api-product-detail'),
    url(r'^users/$', UserList.as_view(), name='api-user-list'),
    url(r'^users/(?P<pk>\d+)/$', UserDetail.as_view(), name='user-detail'),
    url(r'^social/friends/$', FriendshipList.as_view(), name='api-social-friends-list'),
    url(r'^social/followers/$', FollowerList.as_view(), name='api-social-follower-list'),
    url(r'^products/by-all-time/$', ProductListOrderByBuyAllTime.as_view(), name='api-get-product-by-all-time'),
    url(r'^products/by-month/$', ProductListOrderByBuyInMonth.as_view(), name='api-get-product-by-month'),
    url(r'^social/friends/(?P<user_id>\d+)/$', FriendshipList.as_view(), name='api-social-friends-list-other-profile'),
    url(r'^social/like/$', action_like, name='api-social-like'),
)

urlpatterns = format_suffix_patterns(
    urlpatterns, allowed=['json', 'api'])
