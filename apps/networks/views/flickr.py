__author__ = 'tqn'
import unicodedata, json, urllib2, urllib
from itertools import chain
from django.core.cache import cache
from django.views.generic import ListView
from django.template import RequestContext
from django.shortcuts import HttpResponse, render_to_response
from django.core.paginator import Paginator
from apps.networks.libraries.api import MediasCommon
from apps.networks.libraries.flickr.flickr_keys import *

class SearchImages(ListView):
    context_object_name = "search_images"
    template_name = 'networks/search_images.html'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(SearchImages, self).get_context_data(**kwargs)
        context['keywords'] = self.request.GET.get('keywords')
        context['active'] = 'flickr'

        return context

    def get_image_url(self, image):

        image_url = None
        for key in ['url_l', 'url_c', 'url_z', 'url_n', 'url_m']:
            if hasattr(image, key):
                image_url = image.get(key)
                break

        return image_url

    def _handling_results(self, images=[]):

        results = []
        for item in images:
            image_url = self.get_image_url(item)
            if image_url:
                try:
                    results.append({
                        'id': item.get('id'),
                        'title': item.get('title'),
                        'thumbnail_url': image_url,
                        'original_url': image_url,
                        'link': item.get('urls'),
                        'description': item.get('description')
                    })
                except Exception, error:
                    pass

        return results
    def _query(self, **kwargs):
        host = kwargs.get('host')
        keywords = kwargs.get('keywords')
        page = kwargs.get('page')
        try:
            api = MediasCommon(host=host)
            images, info = api.search({'api_key': API_KEY, 'keywords': keywords, 'max_results': 100, 'page': page})
        except Exception, error:
            images, info = [], {}

        return images, info

    def _do_queryset(self, host, keywords):

        try:
            converting = unicodedata.normalize('NFKD', keywords).encode('ascii', 'ignore')
            cache_key_name = '%s_%s' % (host, converting.replace(' ', '_').lower())
            images = cache.get(cache_key_name)

            need_search = False
            if images is None:
                need_search = True
            elif len(images) == 0:
                need_search = True
            else:
                p = Paginator(images, self.paginate_by)
                current_page = self.request.GET.get('page')
                if p.num_pages == int(current_page):
                    next_page = int(len(images)/100) + 1
                    imgs, info = self._query(host=host, keywords=keywords, page=next_page)
                    limit_pages = 25
                    if info.get('total') < limit_pages:
                        limit_pages = info.get('total')
                    if next_page <= limit_pages:
                        cache.delete(cache_key_name)
                        images_plus = self._handling_results(images=imgs)
                        images = list(chain(images, images_plus))
                        cache.set(cache_key_name, images, 86400)

            if need_search:
                images, info = self._query(host=host, keywords=keywords, page=1)
                images = self._handling_results(images=images)
                cache.set(cache_key_name, images, 86400)

        except Exception, error:
            images = []

        return images


    def get_queryset(self):
        keywords = self.request.GET.get('keywords')
        images = self._do_queryset(host='flickr', keywords=keywords)
        return images



def search_images_testing(request):
    cache.clear()

    try:

        url = 'https://api.vineapp.com/timelines/tags/travel?page=2'
        params = urllib.urlencode({'page': 2})
        req = urllib2.Request(url)
        string = urllib2.urlopen(req).read()
        data = json.loads(string)

    except urllib2.HTTPError as e:
        pass

    return render_to_response('networks/flickr/testing.html', {
        'data': data
    }, context_instance=RequestContext(request))