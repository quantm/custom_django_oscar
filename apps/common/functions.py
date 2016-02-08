#coding: utf-8

import os, json, urllib, urllib2, time, hashlib, cStringIO, string, PIL.Image as Image, logging
from datetime import datetime
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string

from apps.common.models import OBJECT_TYPE
from apps.customer.models import Notification
from settings import DEFAULT_URL, MEDIA_ROOT, OSCAR_IMAGE_FOLDER, VIDEO_THUMB
from core.models import User
def handle_uploaded_file(files, tempDir, name, min_size, base_width):
    from PIL import Image
    img = files[0]
    file_type = img.content_type.split('/')[1] if img.content_type != '' else ''
    if file_type not in ('png', 'jpeg', 'jpg', ''):
        return _('You should upload an image file')


    #Check image type
    try:
        tempFile = Image.open(img)
        size = tempFile.size
        if size[0] < min_size or size[1] < min_size:
            return _('Upload image file size should be at least 200x200')

    except Exception, error:
        logging.exception(error)
        return _('System error')

    f = tempDir + name + '.png'
    f = f.encode('ascii', 'ignore')
    destination = open(f, 'wb+')
    for chunk in img.chunks():
        destination.write(chunk)
    destination.close()

    img = Image.open(f)
    best_size = (400, 400)
    img.thumbnail( best_size, Image.ANTIALIAS)
    img.save(f, "JPEG", quality=80, optimize=True, progressive=True)

    tempFile.save(tempDir + name + '_original' + '.png')
    return ''


def send_email(email_from, email_to, subject, html_content):
    try:
        msg = EmailMessage(subject, html_content, email_from, [email_to])
        msg.content_subtype = "html"
        msg.send()
    except Exception, ex:
        logging.exception(ex)
        return False
    return True

def notification_ready_unread(recipient_id, sender_id=None, type=OBJECT_TYPE._REQUEST_FOLLOWER):
    from apps.customer.models import Notification
    notify = Notification.objects.filter(recipient_id=recipient_id, sender_id=sender_id, date_read=None, type=type)
    if len(notify) > 0:
        return True
    return False


def send_notification(recipient_id, sender_id=None, object_id=None,
                      type=OBJECT_TYPE._MESSAGE_NORMAL, notify=True, mail=False, mobile=False):
    sender_fullname = 'Site Admin'
    sender_email = 'contact@demo-oscar.com'
    subject = 'You have a notification'
    notification_body = ''
    email_body_html = ''

    if sender_id:
        sender = User.objects.filter(id=sender_id)[0]
        sender_fullname = sender.get_full_name()
        sender_id = sender.id
        sender_email = sender.email

    recipient = User.objects.filter(id=recipient_id)[0]

    #Process by OBJECT_TYPE And Template Email Here
    if type == OBJECT_TYPE._REQUEST_FRIEND:
        obj = User.objects.filter(id=object_id)[0]
        if sender_id:
            subject = _('Request friend from ') + obj.get_full_name()
        else:
            subject = obj.get_full_name() +  _(' accept friend with you')

    if type == OBJECT_TYPE._REQUEST_FOLLOWER:
        subject = sender_fullname + _(' now is following you')

    if type == OBJECT_TYPE._INVITE_COLLECTION:
        subject = sender_fullname + _(' invite you edit the collection')
        if mail:
            data = {'default_url': DEFAULT_URL, 'object_id': object_id}
            email_body_html = render_to_string('common/email/invite_edit_collection.html', data)

    if type == OBJECT_TYPE._SHARE_COLLECTION:
        subject = sender_fullname + _(' has shared the collection with you')
        if mail:
            data = {'default_url': DEFAULT_URL, 'object_id': object_id}
            email_body_html = render_to_string('common/email/share_collection.html', data)

    if type == OBJECT_TYPE._HASHTAG_MENTION:
        subject = sender_fullname + _(' has mentioned you')

    if type == OBJECT_TYPE._MY_EVENT_NOTIFICATION:
        subject = sender_fullname + _(' has shared event with you')

    if type == OBJECT_TYPE._CELERY_EVENT_NOTIFICATION:
        subject = _('Tomorrow') + "is" + sender_fullname + '`s event'

    if type == OBJECT_TYPE._MY_WALL_NOTIFICATION:
        subject = sender_fullname + _(' has reply to your post')

    if type == OBJECT_TYPE._HASHTAG_MY_WALL_POST:
        subject = sender_fullname + _(' has mention you in the conversation')

    #Do with notify, email, mobile here
    if notify:
        Notification(recipient_id=recipient_id, sender_id=sender_id, subject=subject,
                     body=notification_body, object_id=object_id, type=type).save()

    if mail:
        email_from = sender_fullname + '<' + sender_email + '>'
        email_to = recipient.email
        send_email(email_from, email_to, subject, email_body_html)


def check_image(image_url):
    img_file = False
    try:
        image_on_web = urllib.urlopen(image_url)
        if image_on_web.headers.maintype == 'image':
            io_file = cStringIO.StringIO(urllib.urlopen(image_url).read())
            img_file = Image.open(io_file)
    except Exception, err:
        pass

    return img_file

def save_image_file(image_url, type):
    result = {"code": 0, "image_url": ''}
    try:
        img_file = check_image(image_url)
        if img_file:
            image_extension = '.' + string.lower(img_file.format)
            image_name = hashlib.md5(b'%s' % time.time()).hexdigest() + image_extension
            if type == 'product':
                image_path = datetime.now().strftime(OSCAR_IMAGE_FOLDER)
            elif type == 'media':
                image_path = datetime.now().strftime(VIDEO_THUMB)

            #Make folder if not exists
            abspath = os.path.abspath(MEDIA_ROOT + image_path)
            if not os.path.exists(abspath):
                os.makedirs(abspath)

            image_full_url = image_path + image_name
            img_file.save(MEDIA_ROOT + image_full_url)

            result = {"code": 1, "image_url": image_full_url}

    except Exception, err:
        pass

    return result

def download_photo(image_url_from_web, product_image_url):
    #need recheck MEDIA_ROOT was configured in settings file
    try:
        image_on_web = urllib.urlopen(image_url_from_web)
        if image_on_web.headers.maintype == 'image':
            buf = image_on_web.read()
            file_path = "%s/%s" % (MEDIA_ROOT, product_image_url)
            arr_path = os.path.split(file_path)
            if not os.path.exists(arr_path[0]):
                os.makedirs(arr_path[0])
            downloaded_image = file(file_path, "wb")
            downloaded_image.write(buf)
            downloaded_image.close()
            image_on_web.close()
        else:
            return False
    except:
        return False
    return True
