import unicodedata, settings
from django.core.cache import cache
from django.views.generic import ListView
from django.shortcuts import render_to_response
from django.template import RequestContext, loader

from apps.networks.libraries.api import MediasCommon


CLIENT_SECRET = settings.YOUTUBE_APPS['CLIENT_SECRET']


class SearchVideos(ListView):
    context_object_name = "search_videos"
    template_name = 'networks/youtube/search_videos.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(SearchVideos, self).get_context_data(**kwargs)
        context['youtube_keywords'] = self.request.GET.get('keywords')
        context['active'] = 'youtube'

        return context

    def get_queryset(self):
        keywords = self.request.GET.get('keywords')
        converting = unicodedata.normalize('NFKD', keywords).encode('ascii', 'ignore')
        cache_key_name = 'youtube_%s' % converting.replace(' ', '_').lower()

        videos = cache.get(cache_key_name)
        need_search = False
        if videos is None:
            need_search = True
        elif len(videos) == 0:
            need_search = True

        if need_search:
            try:
                api = MediasCommon(host='youtube', client_secret=CLIENT_SECRET)
                videos = api.search({'keywords': keywords, 'max_results': 50})
                cache.set(cache_key_name, videos, 86400)
            except Exception, error:
                pass

        return videos

def youtube_upload_widget(request):
    return render_to_response('networks/youtube/make_a_video.html', {
    }, context_instance=RequestContext(request))