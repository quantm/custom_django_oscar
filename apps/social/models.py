from django.db import models
from apps.common.models import OBJECT_TYPE
from apps.common.functions import send_notification
from apps.collection.models.media import CollectionMedia
from apps.catalogue.models import Product
from django.utils.translation import ugettext_lazy as _
from itertools import chain
from core.models import User


class SocialHashTag (models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, default=0)
    image = models.CharField(max_length=255, null=True, blank=True, default=0)
    date_created = models.DateTimeField(_('Create date'), auto_now_add=True, editable=False)
    @staticmethod
    def save_mention(name, user, object_id):
        for user_mention in User.objects.filter(username=name):
            send_notification(sender_id=user, recipient_id=user_mention.id,
                              object_id=object_id, type=OBJECT_TYPE._HASHTAG_MENTION, mail=False)
        return name

    @staticmethod
    def save_hashtag(name, object_id, obj_type, hash_tag_thumb):
        hash_tag = SocialHashTag(name=name, image=hash_tag_thumb)
        if SocialHashTag.objects.filter(name=name).count() == 0:
            hash_tag.save()
        for hash_tag_obj in SocialHashTag.objects.filter(name=name):
            if obj_type != 41:
                hash_tag_obj_ = SocialHashTagObject(object_id=object_id,
                                                    hashtag_id=hash_tag_obj.id,
                                                    type=obj_type)
                hash_tag_obj_.save()
        return name

    class Meta:
        db_table = u'social_hashtag'


class SocialHashTagObject(models.Model):
    object_id = models.IntegerField(max_length=128, null=True, blank=True, default=0)
    hashtag = models.ForeignKey(SocialHashTag)
    type = models.IntegerField(max_length=255, null=True, blank=True, default=0)

    class Meta:
        db_table = u'social_hashtag_object'


class SocialFriendShip(models.Model):
    user_self = models.ForeignKey(User, related_name='user_self')
    user_obj = models.ForeignKey(User, related_name='user_obj')
    type = models.IntegerField(max_length=32, blank=True, null=True)

    @staticmethod
    def get_friend_list(user):
        #query = ('SELECT f.* FROM social_friendship f JOIN social_friendship c ON c.user_self_id = f.user_obj_id AND c.user_obj_id = f.user_self_id AND f."type" = %d AND c."type" = %d WHERE f.user_self_id = %d') % (OBJECT_TYPE._REQUEST_FRIEND, OBJECT_TYPE._REQUEST_FRIEND, user.id)
        #friends = SocialFriendShip.objects.raw(query)
        #return list(friends)
        friends = SocialFriendShip.objects.extra(tables=['"social_friendship" AS "c"'],
                                                 where=['"c"."user_self_id" = "social_friendship"."user_obj_id"',
                                                        '"c"."user_obj_id" = "social_friendship"."user_self_id"',
                                                        ('"social_friendship"."type" = %d') % (OBJECT_TYPE._REQUEST_FRIEND),
                                                        ('"c"."type" = %d') % (OBJECT_TYPE._REQUEST_FRIEND),
                                                        ('"social_friendship"."user_self_id" = %d') % (user.id)]).select_related()
        return friends

    @staticmethod
    def get_follower_list(user):
        follower = SocialFriendShip.objects.filter(user_obj=user, type=OBJECT_TYPE._REQUEST_FOLLOWER).select_related()
        return follower

    @staticmethod
    def get_event_participant(event_id):
        query_participant = 'SELECT social.id, social.user_share_id as user_obj_id, ' \
                    'social.user_owner as user_self_id FROM social_event_activity social WHERE social.event_id ='+event_id
        query_owner = "SELECT social.id, social.user_owner as user_obj_id FROM social_event_activity social WHERE social.event_id ="+event_id+" LIMIT 1"
        event_participant = SocialFriendShip.objects.raw(query_participant)
        owner_participant = SocialFriendShip.objects.raw(query_owner)
        return list(chain(event_participant, owner_participant))

    def to_json_obj(self):
        dict = {
                    'id': self.user_obj.id,
                    'email': self.user_obj.email,
                    'is_active': self.user_obj.is_active,
                    'full_name': self.user_obj.get_full_name(),
                    'is_staff': self.user_obj.is_staff,
                    'last_login': self.user_obj.last_login,
                    'date_joined': self.user_obj.date_joined,
                    'avatar': self.user_obj.get_avatar_src_full_url()
                }
        return (dict)

    def to_json_self(self):
        dict = {
                    'id': self.user_self.id,
                    'email': self.user_self.email,
                    'is_active': self.user_self.is_active,
                    'full_name': self.user_self.get_full_name(),
                    'is_staff': self.user_self.is_staff,
                    'last_login': self.user_self.last_login,
                    'date_joined': self.user_self.date_joined,
                    'avatar': self.user_self.get_avatar_src_full_url()
                }
        return (dict)

    class Meta:
        unique_together = ('user_self', 'user_obj', 'type')
        db_table = u'social_friendship'


class SocialPromote(models.Model):
    product = models.ForeignKey(Product, related_name='fk_promote_product')
    user = models.ForeignKey(User, related_name='fk_promote_user', null=True)
    media = models.ForeignKey(CollectionMedia, related_name='fk_promote_media', null=True)
    text = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        unique_together = ('product', 'user')
        db_table = u'social_promote'


class MyEvent(models.Model):
    name = models.CharField(max_length=255, null=True)
    date_created = models.DateField(_('Create date'),)
    description = models.CharField(max_length=1024, null=True)
    participants_amount = models.IntegerField(max_length=128, null=True)
    user = models.ForeignKey(User, editable=False)

    class Meta:
        db_table = u'social_event'


class MyEventObject(models.Model):
    event = models.ForeignKey(MyEvent)
    user_owner = models.IntegerField(_('Creator'), default=0, null=True, max_length=128)
    user_share_id = models.IntegerField(_('Share'), default=0, null=True, max_length=128)
    update = models.DateField(_('Update date'), auto_now_add=True, editable=False)
    is_shared = models.IntegerField(_('Is edited'), default=0, null=True, max_length=128)

    class Meta:
        db_table = u'social_event_activity'


class SocialMessage(models.Model):
    content = models.CharField(max_length=1024, null=True)
    user = models.ForeignKey(User, related_name='user')
    friend = models.ForeignKey(User, related_name='friend')
    type = models.CharField(max_length=1024, null=True)
    create_date = models.DateTimeField(auto_now_add=True, max_length=128)
    message_id = models.IntegerField(null=True, default=0)
    object_id = models.IntegerField(null=True, default=0)

    class Meta:
        db_table = u'social_message'


class SocialLike(models.Model):
    object_id = models.IntegerField(null=False)
    user = models.ForeignKey(User)
    type = models.IntegerField(null=True, max_length=32)

    @staticmethod
    def get_like_count(object_id, type):
        return SocialLike.objects.filter(object_id=object_id, type=type).count()

    @staticmethod
    def is_liked(object_id, user_id, type):
        liked = SocialLike.objects.filter(object_id=object_id, user_id = user_id, type=type)
        if liked:
            return True
        return False

    class Meta:
        unique_together = ('object_id', 'user', 'type')
        db_table = u'social_like'


from .receivers import *
