
import itertools, urllib2, json
from settings import PHOTOBUCKET_APPS
from instagram.client import InstagramAPI
from .youtube.search import YoutubeSearch
from .pinterest.pinterest import Pinterest
from .flickr.objects import Photo as Flickr
from .photobucket import Search as SearchAPI


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class MediasCommon(list):
    host = None
    client_id = None
    client_secret = None
    access_token = None
    timeout = None

    def __init__(self, host=None, client_id=None, client_secret=None, access_token=None, timeout=None):
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.timeout = timeout

    def _instagram(self, args):
        api = InstagramAPI(client_id=self.client_id, client_secret=self.client_secret)
        tags = args.keywords.split(' ')
        try:
            images = []
            for tag in tags:
                imgs, str_next = api.tag_recent_media(tag_name=str(tag), count=args.max_results)
                images = list(itertools.chain(images, imgs))
        except Exception, error:
            images = []

        return images

    def _flickr(self, args):
        try:
            results = Flickr.search(
                api_key=args.api_key,
                extras=['description', 'url_l', 'url_c', 'url_z', 'url_n', 'url_m'],
                text=args.keywords,
                per_page=args.max_results,
                page=args.page
            )
            info = results.info
            images = results.data
        except Exception, error:
            images, info = [], {}

        return images, info

    def _vine(self, args):
        try:
            url = 'https://api.vineapp.com/timelines/tags/%s?page=%d' % (args.keywords, args.page)
            req = urllib2.Request(url)
            string = urllib2.urlopen(req).read()
            data = json.loads(string)
            videos = data['data'].get('records')
            info = {
                'count': data['data'].get('count'),
                'next': data['data'].get('nextPage'),
                'previous': data['data'].get('previousPage')
            }
        except Exception, error:
            videos, info = [], {}

        return videos, info

    def _photobucket(self, args):
        key = PHOTOBUCKET_APPS.get('KEY')
        secret = PHOTOBUCKET_APPS.get('SECRET')
        num = page = offset = perpage = recentfirst = secondaryperpage = None
        if hasattr(args, 'num'):
            num = args.num
        if hasattr(args, 'page'):
            page = args.page
        if hasattr(args, 'offset'):
            offset = args.offset
        if hasattr(args, 'perpage'):
            perpage = args.perpage
        if hasattr(args, 'recentfirst'):
            recentfirst = args.recentfirst
        if hasattr(args, 'secondaryperpage'):
            secondaryperpage = args.secondaryperpage

        try:
            api = SearchAPI(key=key, secret=secret)
            images, attributes = api.images(keywords=args.keywords,
                                            num=num,
                                            page=page,
                                            offset=offset,
                                            perpage=perpage,
                                            recentfirst=recentfirst,
                                            secondaryperpage=secondaryperpage)
        except Exception, error:
            images, attributes = [], {}

        return images, attributes

    def search(self, *args):
        medias = []
        arg = Struct(**args[0])

        if self.host == 'youtube':
            api = YoutubeSearch(key=self.client_secret)
            medias = api.search(arg)

        elif self.host == 'instagram':
            medias = self._instagram(arg)

        elif self.host == 'pinterest':
            api = Pinterest()
            medias = api.search(arg)

        elif self.host == 'flickr':
            medias = self._flickr(arg)

        elif self.host == 'photobucket':
            medias = self._photobucket(arg)

        elif self.host == 'vine':
            medias = self._vine(arg)

        return medias