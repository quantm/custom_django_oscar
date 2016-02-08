import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractProductImage
from core.models import User


class Product(AbstractProduct):
    user = models.ForeignKey(User, blank=True, null=True)
    buy_count_all_time = models.IntegerField(default=0, null=True, max_length=32)
    buy_count_in_month = models.IntegerField(default=0, null=True, max_length=32)

    def get_price(self):
        stock = self.stockrecords.filter(Q(selected_partner=1))
        return stock[0].price_excl_tax

    def get_original_img_url(self):
        image = self.primary_image()
        return image.original.url

    def get_thumb_img_url(self):
        from sorl.thumbnail import get_thumbnail
        image = self.primary_image()
        thumb = get_thumbnail(image.original.name, '480x480')
        return thumb.url

    def image(self):
        images = self.images.all()
        str_image = ''
        if len(images) > 0:
            str_image = images[0].none_watermark

        return str_image
    image.short_description = _("Image")

    def type(self):
        return 'product'
    type.short_description = _("Type")

    def get_image_display(self):
        return self.image


class ProductImage(AbstractProductImage):
    none_watermark = models.ImageField(_("Image none watermark"), upload_to=settings.OSCAR_IMAGE_FOLDER,
                                               max_length=255, blank=True, null=True, default='',
       help_text=_("""An image has a copy none watermark to using in collection view function"""))
