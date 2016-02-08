from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.collection.models import CollectionSetElement
from .models import SocialPromote
from django.utils.timezone import now
from apps.catalogue.models import ProductImage, Product
from apps.social.views import get_mention_hashtag
from apps.common.models import OBJECT_TYPE
from apps.collection.models.media import CollectionMedia

@receiver(post_save, sender=CollectionSetElement)
def do_save_promote(sender, instance=None, created=False, **kwargs):
    try:
        if created:
            if instance.type == 'product':
                current_user = instance.set.user
                product_id = instance.object_id
                text = None
                media_id = None
                social_promote = SocialPromote.objects.filter(product_id=product_id, user_id=current_user.id)
                if social_promote:
                    social_promote.update(media=media_id, text=text, create_date=now())
                    #social_id = social_promote[0].id
                else:
                    social = SocialPromote(product_id=product_id, user_id=current_user.id, media_id=media_id, text=text)
                    social.save()
                    #social_id = social.pk
    except Exception, err:
        pass


@receiver(post_save, sender=Product)
def do_save_mention_hashtag_with_product(sender, instance=None, created=False, **kwargs):
    try:
        if created:
            prod_image_url = None
            prod_desc = instance.description
            user_id = instance.user.id

            get_mention_hashtag("client", OBJECT_TYPE._HASHTAG_BOOKMARK_PRODUCT, prod_desc, instance.id, prod_image_url, user_id)

    except Exception, err:
        pass


@receiver(post_save, sender=ProductImage)
def do_save_mention_hashtag_with_product_image(sender, instance=None, created=False, **kwargs):
    try:
        if created:
            product = instance.product
            prod_image_url = instance.original.url
            prod_desc = product.description
            user_id = product.user.id

            get_mention_hashtag("client", OBJECT_TYPE._HASHTAG_BOOKMARK_PRODUCT, prod_desc, product.id, prod_image_url, user_id)

    except Exception, err:
        pass

@receiver(post_save, sender=CollectionMedia)
def do_save_mention_hashtag_with_media(sender, instance=None, created=False, **kwargs):
    try:
        if created:
            get_mention_hashtag("client", OBJECT_TYPE._HASHTAG_BOOKMARK_IMAGE, instance.description, instance.pk, instance.image.name, instance.user.id)
    except Exception, err:
        pass

