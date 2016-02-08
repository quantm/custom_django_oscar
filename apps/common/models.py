from django.db import models


class OBJECT_TYPE():
    #Collection Type (1 - 9)
    _SHARE_COLLECTION = 1
    _INVITE_COLLECTION = 2

    #Friendship Type (10 - 19)
    _REQUEST_FRIEND = 10
    _REQUEST_FOLLOWER = 12

    #Message Type (20 - 29)
    _MESSAGE_NORMAL = 20
    _MESSAGE_SYSTEM = 21

    #Mobile Type (30 - 39)

    #Hashtag Mention (40 - 49)
    _HASHTAG_MENTION = 40
    _HASHTAG_COLLECTION_COMMENT = 41
    _HASHTAG_BOOKMARK_IMAGE = 46
    _HASHTAG_BOOKMARK_VIDEO = 45
    _HASHTAG_BOOKMARK_PRODUCT = 47
    _HASHTAG_DASHBOARD_PRODUCT = 43
    _HASHTAG_COMMENT_THUMB = 44
    _HASHTAG_PROMOTE_TEXT = 48
    _HASHTAG_MY_WALL_POST = 49

    #Social My Event (50-55)
    _MY_EVENT_NOT_YET_SHARE = 50
    _MY_EVENT_NOTIFICATION = 51
    _CELERY_EVENT_NOTIFICATION = 52

    #Social My Wall (60-65)
    _MY_WALL_NOTIFICATION = 60

    #Social LIKE
    _LIKE_PROMOTE_PRODUCT = 100
    _LIKE_LIST = 101
    _LIKE_MAGAZINE = 102
    _LIKE_USER = 103
    _LIKE_COMMENT = 104

    #Comment
    _MY_WALL_TYPE = "wall"
    _COLLECTION_TYPE = "collection"
    _MY_WALL_OBJ_FRIEND_POST = -1