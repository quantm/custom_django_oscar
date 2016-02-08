#__author__ = 'tqn'
import urllib2
from django.db import models
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.files import ImageFieldFile, FileField

from settings import VIDEO_THUMB
from core.models import User
from apps.common.functions import save_image_file


STATUS_CHOICES = (
    ('p', 'Published'),
    ('w', 'Withdrawn'),
    ('e', 'Deleted'),
)

MEDIA_TYPE = (
    ('image', 'Image'),
    ('video', 'Video')
)


class CollectionMedia(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255, unique=False)
    type = models.CharField(_('Media Type'), max_length=50, choices=MEDIA_TYPE)
    code = models.CharField(_('Video Code'), max_length=255, null=True, default='')
    image = models.ImageField(_('Thumbnail'), upload_to=VIDEO_THUMB,
                              max_length=255, blank=True, null=True)
    description = models.TextField(_('Description'), null=True, blank=True)
    user = models.ForeignKey(User, editable=False)
    create = models.DateTimeField(_('Create date'), auto_now_add=True, editable=False)
    view = models.IntegerField(_('View counter'), max_length=128, blank=True, default=0)
    like = models.IntegerField(_('Like counter'), max_length=128, blank=True, default=0)
    status = models.CharField(_('Status'), max_length=1, choices=STATUS_CHOICES, default="p")

    def __unicode__(self):  # Python 3: def __str__(self):
        return u'%s %s' % (self.title, self.description)

    @models.permalink
    def get_absolute_url(self):

        if self.type == 'video':
            return ('video-detail', (), {'pk': self.id})
        else:
            return ('my-images', (), {})

    def get_code_display(self):
        if self.slug != 'vine':
            return self.code
        else:
            return self.code

    def get_image_display(self):
        if self.type == 'video' and not hasattr(self.image, 'url'):
            if self._video_update_thumbnail():
                return self.image
            else:
                return ImageFieldFile(instance=None, field=FileField(), name='processing.jpg')
        else:
            return self.image

    def _video_update_thumbnail(self):
        cache.clear()
        try:
            thumbnail_url = 'http://img.youtube.com/vi/%s/hqdefault.jpg' % self.code.strip()
            req = urllib2.Request(thumbnail_url)
            obj = urllib2.urlopen(req).read()
            image_saved = save_image_file(thumbnail_url, 'media')
            if image_saved.get('code') == 1:
                self.image = image_saved.get('image_url')
                self.save(update_fields=['image'])
            return True
        except Exception, error:
            return False

    class Meta:
        db_table = u'collection_media'
        app_label = 'collection'

