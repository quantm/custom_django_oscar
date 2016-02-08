#!/usr/bin/python

from apiclient.discovery import build
from optparse import OptionParser

# Set DEVELOPER_KEY to the "API key" value from the "Access" tab of the
# Google APIs Console http://code.google.com/apis/console#access
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyBBFZWEYd07X6mIf44b6k1TITfCeR6QTII"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  search_response = youtube.search().list(
    q=options.q,
    part="id,snippet",
    maxResults=options.maxResults
  ).execute()

  videos = []
  channels = []
  playlists = []

  for search_result in search_response.get("items", []):
      if search_result["id"]["kind"] == "youtube#video":
          #videos.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["videoId"]))
          videos.append({
              'id': search_result["id"]["videoId"],
              'title': search_result["snippet"]["title"]
          })

      elif search_result["id"]["kind"] == "youtube#channel":
          #channels.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["channelId"]))
          channels.append({
              'id': search_result["id"]["channelId"],
              'title': search_result["snippet"]["title"]
          })

      elif search_result["id"]["kind"] == "youtube#playlist":
          #playlists.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["playlistId"]))
          playlists.append({
              'id': search_result["id"]["playlistId"],
              'title': search_result["snippet"]["title"]
          })


  return {
      'videos': videos,
      'channels': channels,
      'playlists': playlists
  }
  #print "Videos:\n", "\n".join(videos), "\n"
  #print "Channels:\n", "\n".join(channels), "\n"
  #print "Playlists:\n", "\n".join(playlists), "\n"


if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("--q", dest="q", help="Search term",
    default="Google")
  parser.add_option("--max-results", dest="maxResults",
    help="Max results", default=25)
  (options, args) = parser.parse_args()

  youtube_search(options)