#__author__ = 'Tam'
from apps.social.models import SocialFriendShip
from apps.common.models import OBJECT_TYPE

# Check Already Requested From Other User
def is_ready_requested(user_self,user_obj):
    ready = SocialFriendShip.objects.filter(user_self=user_obj, user_obj=user_self, type=OBJECT_TYPE._REQUEST_FRIEND)
    if len(ready) > 0:
        return True
    return False

# Check Already Requested From this User
def is_requested(user_self,user_obj):
    ready = SocialFriendShip.objects.filter(user_self=user_self, user_obj=user_obj, type=OBJECT_TYPE._REQUEST_FRIEND)
    if len(ready) > 0:
        return True
    return False

def is_friend(user_self,user_obj):
    ready_requested = is_ready_requested(user_self,user_obj)
    requested = is_requested(user_self,user_obj)
    dict = {
        'ready_requested': ready_requested,
        'requested': requested,
        'is_friend': False
    }
    if ready_requested and requested:
        dict['is_friend'] = True

    return dict

def is_follower(user_self,user_obj):
    ready = SocialFriendShip.objects.filter(user_self=user_self, user_obj=user_obj, type=OBJECT_TYPE._REQUEST_FOLLOWER)
    if len(ready) > 0:
        return True
    return False


