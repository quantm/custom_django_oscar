#__author__ = 'tqn'

from django.db import models
from django.utils.translation import ugettext_lazy as _
from apps.catalogue.models import Product
from media import CollectionMedia

from core.models import User

STATUS_CHOICES = (
    ('d', 'Draft'),
    ('p', 'Published'),
    ('c', 'Create'),
    ('e', 'Deleted'),
    ('f', 'Default'),
)

COLLECTION_TYPE = (
    ('list', _('List')),
    ('collection', _('Collection'))
)


class CollectionSet(models.Model):
    name = models.CharField(_('Collection name'), max_length=255, blank=True)
    user = models.ForeignKey(User, editable=False)
    type = models.CharField(_('Type'), max_length=50, choices=COLLECTION_TYPE, null=True, default='')
    thumb = models.CharField(_('Image'), max_length=255, blank=True, null=True, default='')
    create = models.DateTimeField(_('Create date'), auto_now_add=True, editable=False)
    view = models.IntegerField(_('View counter'), max_length=128, null=True, blank=True, default=0)
    status = models.CharField(_('Status'), max_length=1, choices=STATUS_CHOICES, default="p")
    default = models.BooleanField(_('Is default'), default=False, blank=True)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name

    class Meta:
        db_table = u'collection_set'
        app_label = 'collection'


class CollectionSetEdit(models.Model):
    set = models.ForeignKey(CollectionSet)
    editor = models.ForeignKey(User, editable=False)
    creator_id = models.IntegerField(_('Creator'), default=0, null=True, max_length=128)
    update = models.DateTimeField(_('Update date'), auto_now_add=True, editable=False)
    is_edited = models.IntegerField(_('Is edited'), default=0, null=True, max_length=128)

    class Meta:
        db_table = u'collection_set_edit'
        app_label = 'collection'


class CollectionSetElement(models.Model):
    object_id = models.IntegerField(_('Object'), max_length=255, null=True, blank=True, default=0)
    set = models.ForeignKey(CollectionSet)
    type = models.CharField(_('Type'), max_length=255, null=False, blank=True)
    style = models.TextField(_('Display style'), null=True, blank=True)
    class_name = models.CharField(_('Class name'), max_length=255, null=True, blank=True)
    content = models.TextField(_('Content'), null=True, blank=True)

    class Meta:
        db_table = u'collection_set_element'
        app_label = 'collection'

    def object(self):
        obj = None
        if self.type == 'product':
            obj = Product.objects.get(pk=self.object_id)
        elif self.type in ['video', 'image']:
            obj = CollectionMedia.objects.get(pk=self.object_id)
        return obj


class CollectionComment(models.Model):
    set = models.ForeignKey(CollectionSet)
    content = models.CharField(max_length=1024, null=True, blank=True)
    user = models.ForeignKey(User)
    user_comment = models.CharField(max_length=255, null=False)

    class Meta:
        db_table = u'collection_comment'
        app_label = 'collection'

#Using at bottom file
from apps.collection.receivers import *