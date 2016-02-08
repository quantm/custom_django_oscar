from apiclient.discovery import build

class YoutubeSearch(list):
    key = None
    version = "v3"
    service_name = "youtube"

    def __init__(self, key=None, version=None, service_name=None):
        self.key = key
        if version is not None:
            self.version = version
        if service_name is not None:
            self.service_name = service_name

    def search(self, args):
        youtube = build(self.service_name, self.version, developerKey=self.key)

        search_response = youtube.search().list(
            q=args.keywords,
            part="id,snippet",
            maxResults=args.max_results
        ).execute()

        videos = []

        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos.append({
                    'id': search_result["id"]["videoId"],
                    'title': search_result["snippet"]["title"]
                })

        return videos

