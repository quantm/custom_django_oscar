#__author__ = 'tqn'

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from apps.catalogue.models import Product



@receiver(post_save, sender=Product)
def keep_catalogue_product_for_user_when_product_created(sender, instance=None, created=False, **kwargs):
    pass


@receiver(pre_delete, sender=Product)
def delete_reference_between_product_and_user(sender, instance=None, **kwargs):
    pass