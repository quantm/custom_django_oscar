#__author__ = 'tqn'

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.collection.models.collection import CollectionSet
from core.models import User

@receiver(post_save, sender=User)
def auto_create_default_list_for_user(sender, instance=None, created=False, **kwargs):
    if created:
        if instance.pk != 1:
            default_list = CollectionSet(name=u'Default', user=instance, type='list', status='f', default=True)
            default_list.save()