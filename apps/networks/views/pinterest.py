__author__ = 'tqn'
import unicodedata
from django.core.cache import cache
from django.views.generic import ListView
from apps.networks.libraries.api import MediasCommon

class SearchImages(ListView):
    context_object_name = "search_images"
    template_name = 'networks/search_images.html'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(SearchImages, self).get_context_data(**kwargs)
        context['keywords'] = self.request.GET.get('keywords')
        context['active'] = 'pinterest'

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
            api = MediasCommon(host=host)
            images = api.search({'keywords': keywords, 'max_results': 100})
            cache.set(cache_key_name, images, 86400)

        return images

    def _handling_results(self, images=[]):

        results = []
        for item in images:
            try:
                results.append({
                    'id': item['id'],
                    'title': item['id'],
                    'thumbnail_url': item['img'],
                    'original_url': item['img'],
                    'link': item['link'],
                    'description': item['desc']
                })
            except Exception, error:
                pass
        return results


    def get_queryset(self):


        keywords = self.request.GET.get('keywords')
        is_ok = True
        try:
            images = self._do_queryset(host='pinterest', keywords=keywords)
        except Exception, error:
            is_ok = False
        if is_ok:
            return self._handling_results(images=images)
        else:
            return []