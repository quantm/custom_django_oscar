import os, urllib, time, hashlib, cStringIO, string, json, re, unicodedata, urllib2
from io import StringIO

import PIL.Image as Image
from django.views.generic import DetailView, ListView
from django.shortcuts import render_to_response, HttpResponse
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _

from oscar.core.utils import slugify
from oscar.apps.customer.mixins import PageTitleMixin

from apps.collection.forms.media import *
from apps.collection.models import *
from apps.common.decorator import *
from apps.common.functions import *

from settings import AVATAR_DIR, MEDIA_ROOT, PRODUCT_ITEM_PER_PAGE, MEDIAS_PER_PAGE, VIDEO_THUMB

def save_video(request):
    message = {
        'code': 0,
        'link': {},
        'back_text': _('Add more Videos'),
        'message': _("Video hasn't been saved"),
    }
    video_form = CollectionVideo_Form(request.POST or None)
    if video_form.is_valid():
        try:
            image_url = urllib.unquote(request.POST.get('image')).decode('utf8')
            saved = save_image_file(image_url, 'media')
            if saved.get('code') == 1:
                title = request.POST.get('title')
                video_slug = slugify(title)
                image_url = saved.get('image_url')
                video_code = request.POST.get('video_code')
                description = request.POST.get('description')
                user = request.user

                video = CollectionMedia(title=title, slug=video_slug, type='video', code=video_code.strip(), image=image_url, description=description, user=user)
                video.save()

                message = {
                    'code': 1,
                    'object_id': video.pk,
                    'hash_tag_thumb_url': image_url,
                    'link': {
                        'url': "/collection/media/video/%s/" % video.pk,
                        'text': _('See the video')
                    },
                    'back_text': _('Add more Videos'),
                    'message': _('Video has been saved'),
                }
        except Exception, err:
            pass

    return message

def get_host_path_of_inside_image(request):
    host_path = ''
    try:
        image_url = request.POST.get('image')
        #Check image of this site with path is static configure
        if 'cp' in request.POST:
            if int(request.POST.get('cp')) == 1:
                m = re.search('http://', image_url)
                if m is None:
                    prefix = 'https://' if request.is_secure() else 'http://'
                    host_path = prefix + request.get_host()

    except Exception, err:
        pass

    return host_path

def do_crop_image(request, image_url):
    #Crop image
    if 'crop' in request.POST:
        try:
            url_original = AVATAR_DIR + 'insert_media_%s' % str(request.user.id) + '_original' + '.png'
            io_data = StringIO(request.POST.get('crop'))
            crop_info = json.load(io_data)
            crop_image(image_url, url_original, crop_info)
        except Exception, err:
            pass

def save_image(request):

    message = {
        'code': 0,
        'link': {},
        'back_text': _('Add more Images'),
        'message': _("Image hasn't been saved"),
    }
    image_form = CollectionImage_Form(request.POST or None)
    if image_form.is_valid():
        try:
            host_path = get_host_path_of_inside_image(request)
            image_url = host_path + request.POST.get('image')
            image_url = urllib.unquote(image_url).decode('utf8')
            saved = save_image_file(image_url, 'media')
            if saved.get('code') == 1:
                title = request.POST.get('title')
                slug = slugify(title)
                description = request.POST.get('description')
                user = request.user
                image_url = saved.get('image_url')
                do_crop_image(request, image_url)
                image = CollectionMedia(title=title, slug=slug, type='image', image=image_url, description=description, user=user)
                image.save()
                message = {
                    'code': 1,
                    'object_id': image.pk,
                    'link': {
                        'url': "/collection/media/images/",
                        'text': _('View the images')
                    },
                    'back_text': _('Add more Images'),
                    'message': _('Image has been saved'),
                }

        except Exception, err:
            pass
    return message

def save_facebook_image(image_params, user):

    image = None
    try:
        title = image_params.get('title')
        slug = slugify(title)
        image_url = image_params.get('url')
        description = image_params.get('description')

        image_url_from_web = urllib.unquote(image_url).decode('utf8')
        image_path = ''
        saved = save_image_file(image_url, 'media')
        if saved.get('code') == 1:
            image_path = saved.get('image_url')

        image = CollectionMedia(title=title, slug=slug, type='image', image=image_path, description=description, user=user)
        image.save()

        return image
    except Exception, err:
        pass

    return image

def save_thumb(image_url_from_web, url_thumb):
    #need recheck MEDIA_ROOT was configured in settings file
    try:
        image_on_web = urllib.urlopen(image_url_from_web)
        if image_on_web.headers.maintype == 'image':
            buf = image_on_web.read()
            #to check dirs
            arr_path = os.path.split(MEDIA_ROOT + url_thumb)
            if not os.path.exists(arr_path[0]):
                os.makedirs(arr_path[0])

            downloaded_image = file(MEDIA_ROOT + url_thumb, "wb")
            downloaded_image.write(buf)

            downloaded_image.close()
            image_on_web.close()
        else:
            return False
    except:
        return False
    return True

def render_thumb_path_and_save(image_url_from_web):
    path_image = ''
    try:
        io_file = cStringIO.StringIO(urllib.urlopen(image_url_from_web).read())
        img_file = Image.open(io_file)

        image_extension = '.' + string.lower(img_file.format)
        image_name = hashlib.md5(b'%s' % time.time()).hexdigest() + image_extension
        path_image = VIDEO_THUMB + image_name

        if os.path.exists(MEDIA_ROOT + path_image):
            path_image = VIDEO_THUMB + hashlib.md5(b'%s' % time.time()).hexdigest() + image_extension

        img_file.save(MEDIA_ROOT + path_image)
    except Exception, error:
        pass

    return path_image

def crop_image(url_thumb, url_original, crop_info):

    try:
        left = int(crop_info['left'])
        top = int(crop_info['top'])
        width = int(crop_info['width'])
        height = int(crop_info['height'])

        image_url_save = MEDIA_ROOT + url_thumb
        original = Image.open(url_original)
        image = Image.open(image_url_save)

        if width >= 200 or height >= 200:
            #calculator cropping size with real image
            real_left = (original.size[0]*left)/image.size[0]
            real_top = (original.size[1]*top)/image.size[1]
            real_width = (original.size[0]*width)/image.size[0]
            real_height = (original.size[1]*height)/image.size[1]

            if original.size[0] < real_width:
                real_width = original.size[0]
            if original.size[1] < real_height:
                real_height = original.size[1]

            crop_box = (real_left, real_top, real_left + real_width, real_top + real_height)
            original = original.crop(crop_box)

        original.save(image_url_save)

    except Exception, error:
        pass

class CollectionVideo_ListView(LoginRequiredMixin, PageTitleMixin, ListView):
    context_object_name = active_tab = "my-videos"
    page_title = _('My Video')
    model = CollectionMedia
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(CollectionVideo_ListView, self).get_context_data(**kwargs)
        return context

    def get_template_names(self):
        if self.request.is_ajax():
            return 'collection/media/my_videos_of_page.html'
        else:
            return 'collection/media/my_videos.html'

    def get_queryset(self):
        return CollectionMedia.objects.filter(user=self.request.user, type='video').order_by('-create')


class CollectionVideoListViewOtherProfile(LoginRequiredMixin, PageTitleMixin, ListView):
    context_object_name = active_tab = "my-videos"
    page_title = _('My Video')
    model = CollectionMedia
    template_name = 'collection/media/video_list_view.html'

    def get_context_data(self, **kwargs):
        context = super(CollectionVideoListViewOtherProfile, self).get_context_data(**kwargs)
        user_id = self.kwargs['user_id']
        view_user = User.objects.get(id=user_id)
        context['view_user'] = view_user
        return context

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        view_user = User.objects.get(id=user_id)
        qs = CollectionMedia.objects.filter(user=view_user, type='video').order_by('-view', 'create')
        return qs

class CollectionVideoOtherProfileDetailView(LoginRequiredMixin, PageTitleMixin, DetailView):
    context_object_name = active_tab = "my-videos"
    page_title = ''
    model = CollectionMedia
    template_name = 'collection/media/video_detail_view.html'

    def get_context_data(self, **kwargs):
        context = super(CollectionVideoOtherProfileDetailView, self).get_context_data(**kwargs)
        current_video = CollectionMedia.objects.get(pk=self.kwargs['pk'])
        context['videos'] = CollectionMedia.objects.filter(user=current_video.user, type='video').exclude(pk=self.kwargs['pk'])
        user_id = self.request.GET['user_id']
        view_user = User.objects.get(id=user_id)
        context['view_user'] = view_user
        return context

class CollectionVideo_DetailView(LoginRequiredMixin, PageTitleMixin, DetailView):
    context_object_name = active_tab = "my-videos"
    page_title = ''
    model = CollectionMedia
    template_name = 'collection/media/video_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CollectionVideo_DetailView, self).get_context_data(**kwargs)
        current_video = CollectionMedia.objects.get(pk=self.kwargs['pk'])
        context['videos'] = CollectionMedia.objects.filter(user=current_video.user, type='video').exclude(pk=self.kwargs['pk'])

        return context


class CollectionImages_ListView(LoginRequiredMixin, PageTitleMixin, ListView):
    context_object_name = active_tab = "my-images"
    page_title = _('My Images')
    model = CollectionMedia
    paginate_by = PRODUCT_ITEM_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super(CollectionImages_ListView, self).get_context_data(**kwargs)
        return context

    def get_template_names(self):
        if self.request.is_ajax():
            return 'collection/media/my_images_of_page.html'
        else:
            return 'collection/media/my_images.html'

    def get_queryset(self):
        qs = CollectionMedia.objects.filter(user=self.request.user, type='image').order_by('-create')
        return qs


class CollectionImagesListViewOtherProfile(LoginRequiredMixin, PageTitleMixin, ListView):
    context_object_name = active_tab = "my-images"
    page_title = _('My Images')
    template_name = 'collection/media/image_list_view.html'
    model = CollectionMedia
    paginate_by = PRODUCT_ITEM_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super(CollectionImagesListViewOtherProfile, self).get_context_data(**kwargs)
        user_id = self.kwargs['user_id']
        view_user = User.objects.get(id=user_id)
        context['view_user'] = view_user
        return context

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        view_user = User.objects.get(id=user_id)
        qs = CollectionMedia.objects.filter(user=view_user, type='image').order_by('create')
        return qs

class CollectionMediaLoad_ListView(LoginRequiredMixin, ListView):
    context_object_name = "my_media"
    template_name = 'collection/media/media_append_to_modal.html'
    model = CollectionMedia
    paginate_by = MEDIAS_PER_PAGE

    def get_context_data(self, **kwargs):

        context = super(CollectionMediaLoad_ListView, self).get_context_data(**kwargs)
        context['type'] = self.kwargs.get('type')
        return context

    def get_queryset(self):
        return CollectionMedia.objects.filter(type=self.kwargs.get('type'), user=self.request.user).order_by('-create')

@LoginRequired
def add_media(request):
    is_video = int(request.POST.get('is_video'))
    if is_video == 1:
        message = save_video(request)
        message['type'] = 'video'
    else:
        message = save_image(request)
        message['type'] = 'image'

    if 'object_id' in message:
        media_obj = CollectionMedia.objects.get(pk=message['object_id'])

        return render_to_response('collection/media/add_media_return.html',
                              {
                                  'media_obj': media_obj,
                                  'message': message
                              }, context_instance=RequestContext(request))
    else:
        return HttpResponse(json.dumps(message))

@LoginRequired
def remove_media(request, pk=None):

    message = {'code': 0, 'message': _("Access denied")}
    media = CollectionMedia.objects.filter(pk=pk)
    if len(media) > 0:
        current_user_id = request.user.id
        if media[0].user.id == current_user_id:
            media.delete()
            message = {'code': 1, 'message': _("Remove successful")}

    return HttpResponse(json.dumps(message), mimetype='application/json')

@LoginRequired
def save_media(request, type=None):
    try:
        user = request.user
        video_code = request.POST.get('id')
        title = request.POST.get('title')
        video_slug = slugify(title)
        if 'vine' in request.POST:
            video_slug = 'vine'
        description = request.POST.get('description') or ''
        image = None
        if 'image' in request.POST:
            image_url = urllib.unquote(request.POST.get('image')).decode('utf8')
            saved = save_image_file(image_url, 'media')
            if saved.get('code') == 1:
                image = saved.get('image_url')

        video = CollectionMedia(title=title, slug=video_slug, type=type, code=video_code.strip(), user=user, description=description, image=image)
        video.save()

        if image is None and video_slug != 'vine':
            video._video_update_thumbnail()

        return render_to_response('collection/media/add_media_return.html',
                                  {
                                      'media_obj': video,
                                      'message': {'code': 1, 'type': type}
                                  }, context_instance=RequestContext(request))
    except Exception, error:
        return HttpResponse(json.dumps({'code': 0, 'type': type}), mimetype='application/json')