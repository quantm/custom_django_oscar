from django.db import models
from django.contrib.auth.models import AbstractUser
from os.path import isfile
from settings import DEFAULT_URL, AVATAR_DIR, STATIC_URL, MEDIA_URL, AVATAR_URL
from django.contrib.staticfiles.templatetags.staticfiles import static
import time


class User(AbstractUser):
    fb_id = models.CharField(max_length=255, unique=True, null=True, blank=True, editable=False)
    profile_url = models.CharField(max_length=255, null=True, blank=True)

    # By Mr.Tam
    def get_avatar_src_full_url(self):
        ts = time.time()
        avatar_url = static('images/no_avatar.png')
        img_avatar = AVATAR_DIR + str(self.id) + '_avatar.png'
        avatar = static(AVATAR_URL + str(self.id) + '_avatar.png') + "?ts=" + str(ts)

        if isfile(img_avatar):
            avatar_url = avatar
        elif self.fb_id:
            avatar_url = 'https://graph.facebook.com/' + str(self.fb_id) + '/picture?width=200&height=200'

        return avatar_url

    @staticmethod
    def get_mention_list(username_str):
        return list(User.objects.filter(username__startswith=str(username_str)))

    def get_full_name(self):
            full_name = '%s %s' % (self.first_name, self.last_name)
            return full_name.strip()

    class Meta:
        db_table = u'core_user'