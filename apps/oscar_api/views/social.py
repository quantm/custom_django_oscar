from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, JSONPRenderer, TemplateHTMLRenderer, BrowsableAPIRenderer
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from apps.oscar_api import serializers
from settings import USER_ITEM_PER_PAGE
from apps.social.models import *
from core.models import User
from django.utils.translation import ugettext as _
from apps.common.decorator import *

class FriendshipList(generics.ListAPIView):
    serializer_class = serializers.FriendShipListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    pagination_serializer_class = serializers.CustomPaginationSerializer
    paginate_by = USER_ITEM_PER_PAGE
    template_name = 'social/friend/ajax_my_friend.html'

    renderer_classes = (JSONRenderer, JSONPRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer,)
    model = SocialFriendShip

    def get_queryset(self):
        user = self.request.user
        user_id = None
        try:
            user_id = self.kwargs['user_id']
        except Exception, err:
            pass

        if user_id:
            user = User.objects.get(id=user_id)

        return SocialFriendShip.get_friend_list(user)


class FollowerList(generics.ListAPIView):
    serializer_class = serializers.FollowerListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    paginate_by = USER_ITEM_PER_PAGE

    renderer_classes = (JSONRenderer,)
    model = SocialFriendShip

    def get_queryset(self):
        return SocialFriendShip.get_follower_list(self.request.user)

@LoginRequired
@api_view(['POST'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def action_like(request):
    data = {
        'error':'',
        'count': 0,
        'action':''
    }
    try:
        current_user = request.user
        if current_user.is_authenticated():
            action = request.POST['action']
            object_id = int(request.POST['object'])
            type = int(request.POST['type'])
            liked = SocialLike.is_liked(object_id, current_user.id, type)
            if action == 'like':
                if liked:
                    data['error'] = _('You are ready liked')
                else:
                    save_like = SocialLike(object_id = object_id, user_id = current_user.id, type = type)
                    save_like.save()
                    data['count'] = SocialLike.get_like_count(object_id, type)
                    data['action'] = 'unlike'
            elif action == 'unlike':
                deleted_like = SocialLike.objects.filter(object_id = object_id, user_id = current_user.id, type = type)
                if deleted_like:
                    deleted_like.delete()
                    data['count'] = SocialLike.get_like_count(object_id, type)
                    data['action'] = 'like'

        else:
            data['error'] = 'Login'
    except Exception, err:
        data['error'] = _('Can not request right now, Please reload page and try again')

    return Response(data)