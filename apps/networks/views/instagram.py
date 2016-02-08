import unicodedata
from settings import INSTAGRAM_APPS

from django.core.cache import cache
from django.views.generic import ListView
from apps.networks.libraries.api import MediasCommon

CLIENT_ID = INSTAGRAM_APPS['CLIENT_ID']
CLIENT_SECRET = INSTAGRAM_APPS['CLIENT_SECRET']

class SearchImages(ListView):
    context_object_name = "search_images"
    template_name = 'networks/search_images.html'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(SearchImages, self).get_context_data(**kwargs)
        context['keywords'] = self.request.GET.get('keywords')
        context['active'] = 'instagram'

        return context

    def _do_queryset(self, host, keywords):

        converting = unicodedata.normalize('NFKD', keywords).encode('ascii', 'ignore')
        cache_key_name = '%s_%s' % (host, converting.replace(' ', '_').lower())
        images = cache.get(cache_key_name)

        need_search = False
        if images is None:
            need_search = True
        elif len(images) == 0:
            need_search = True

        if need_search:
            api = MediasCommon(host=host, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
            images = api.search({'keywords': keywords, 'max_results': 100})
            cache.set(cache_key_name, images, 86400)

        return images

    def _handling_results(self, images=[]):
        results = []
        for item in images:
            item_data = {
                'id': item.id,
                'title': item.id,
                'thumbnail_url': item.images['low_resolution'].url,
                'original_url': item.images['standard_resolution'].url,
                'link': item.link,
                'description': ''
            }

            if item.caption is not None:
                item_data['description'] = item.caption.text

            results.append(item_data)

        return results


    def get_queryset(self):
        keywords = self.request.GET.get('keywords')
        images = self._do_queryset(host='instagram', keywords=keywords)
        return self._handling_results(images=images)