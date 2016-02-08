from django.views.generic import ListView
from apps.networks.libraries.api import MediasCommon

class SearchVideos(ListView):
    context_object_name = "search_videos"
    template_name = 'networks/vine/search_videos.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(SearchVideos, self).get_context_data(**kwargs)
        return context

    def _handling_results(self, videos=[], info={}):
        count = info.get('count') or 0
        if count > 500:
            count = 500
        page = info.get('page') or 1
        results = range(count)
        i = 0
        for item in videos:
            data = {
                'id': item.get('postId'),
                'title': item.get('postId'),
                'thumbnail_url': item.get('thumbnailUrl').split('?versionId')[0],
                'video_url': item.get('videoUrl').split('?versionId')[0],
                'link': item.get('permalinkUrl'),
                'description': item.get('description')
            }

            #index = (page-1)*len(videos) + i
            index = (page-1)*self.paginate_by + i
            results[index] = data
            i += 1

        return results


    def get_queryset(self):
        results = []
        keywords = self.request.GET.get('keywords')
        page = self.request.GET.get('page') or 1
        tags = keywords.split(' ')
        if len(tags) > 0:
            api = MediasCommon(host='vine')
            videos, info = api.search({'keywords': tags[0], 'page': int(page)})
            info['page'] = int(page)
            results = self._handling_results(videos=videos, info=info)

        return results