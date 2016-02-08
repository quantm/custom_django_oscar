#__author__ = 'tqn'
from django.db.models.signals import post_save
from django.dispatch import receiver
from oscar.apps.catalogue.models import ProductImage
from django.contrib.sites.models import Site

#Using for wartermark app
import os, urllib, cStringIO, datetime, hashlib
from PIL import Image, ImageFont, ImageDraw
from settings import *

@receiver(post_save, sender=ProductImage)
def make_wartermark_for_image(sender, instance=None, created=False, **kwargs):
    if instance.original:
        if kwargs['update_fields'] is None or 'none_watermark' not in kwargs['update_fields']:
            product_image = instance
            update_none_watermark_field(product_image)
            #make_watermark(product_image)

def update_none_watermark_field(product_image):
    try:
        product_image_path = product_image.original.name
        file_ext = os.path.splitext(product_image_path)
        file_nm = hash(os.path.basename(file_ext[0]))
        new_image_path = datetime.datetime.now().strftime(OSCAR_IMAGE_FOLDER) + hashlib.md5(b'%s' % file_nm).hexdigest() + file_ext[1]

        image = Image.open(product_image.original.path)
        image.save(os.path.abspath(MEDIA_ROOT + new_image_path))

        if hasattr(product_image, 'none_watermark'):
            product_image.none_watermark = new_image_path
            product_image.save(update_fields=['none_watermark'])

    except Exception, err:
        pass

def make_watermark(product_image):

    try:
        default_logo_to_watermark = WATERMARK_LOGO
        file_io = cStringIO.StringIO(urllib.urlopen(default_logo_to_watermark).read())
        logo_obj = Image.open(file_io)
        logo_w, logo_h = logo_obj.size
        #Set position to put text on the image
        text_position = (16, logo_h + 32)
        #load font for text
        font = ImageFont.truetype(FONT_PATH, WATERMARK_TEXT_FONT_SIZE)

        #Get image file from data
        prod_image_file = product_image.original.path
        prod_image_url = os.path.abspath(prod_image_file)

        #Read image file from data
        background = Image.open(prod_image_url)
        bg_w, bg_h = background.size
        #
        draw = ImageDraw.Draw(background)
        #Put text on the image

        draw.text(text_position, WATERMARK_TEXT, font=font, fill=int(WATERMARK_TEXT_COLOR))

        #Check site image and logo
        if (bg_w <= logo_w) or (bg_h <= logo_h):
            new_size = (bg_w/4-16, bg_h/4-16)
            logo_obj = logo_obj.resize(new_size, Image.ANTIALIAS)
        elif (bg_w-logo_w) < 16 or (bg_h-logo_h) < 16:
            new_size = (logo_w/2-16, logo_h/2-16)
            logo_obj = logo_obj.resize(new_size, Image.ANTIALIAS)

        #put logo on the image
        background.paste(logo_obj, WATERMARK_LOGO_POSITION, logo_obj)
        path_to_save = os.path.abspath(MEDIA_ROOT + product_image.original.name)
        background.save(path_to_save)

    except Exception, err:
        pass