__author__ = 'tqn'
import unicodedata, json, urllib2
from itertools import chain
from django.core.cache import cache
from django.views.generic import ListView
from django.shortcuts import HttpResponse
from django.core.paginator import Paginator
from apps.networks.libraries.api import MediasCommon
from apps.networks.libraries.photobucket import Search as SearchAPI

class SearchImages(ListView):
    context_object_name = "search_images"
    template_name = 'networks/search_images.html'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(SearchImages, self).get_context_data(**kwargs)
        context['keywords'] = self.request.GET.get('keywords')
        context['active'] = 'photobucket'

        return context

    def _handling_results(self, images=[]):

        results = []
        for item in images:
            try:
                title = item.get('_attribs').get('uploaddate')
                if item.get('title') != '':
                    title = item.get('title')

                results.append({
                    'id': item.get('_attribs').get('uploaddate'),
                    'title': title,
                    'thumbnail_url': item.get('url'),
                    'original_url': item.get('url'),
                    'link': item.get('url'),
                    'description': title
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
            images, attrs = api.search({'keywords': keywords, 'perpage': 100, 'page': page})
        except Exception, error:
            images, attrs = [], {}

        return images, attrs

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
                    if info.get('totalpages') < limit_pages:
                        limit_pages = info.get('totalpages')
                    if next_page <= limit_pages:
                        cache.delete(cache_key_name)
                        images_plus = self._handling_results(images=imgs)
                        images = list(chain(images, images_plus))
                        cache.set(cache_key_name, images, 86400)

            if need_search:
                imgs, info = self._query(host=host, keywords=keywords, page=1)
                images = self._handling_results(images=imgs)
                cache.set(cache_key_name, images, 86400)

        except Exception, error:
            images = []

        return images


    def get_queryset(self):
        try:
            keywords = self.request.GET.get('keywords')
            images = self._do_queryset(host='photobucket', keywords=keywords)
        except Exception, error:
            images = []

        return images
