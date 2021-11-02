from __future__ import unicode_literals
import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse
from configparser import ConfigParser

google_api_key = "AIzaSyB3jQtRAPtSufHjm-UcZlul25Rv9H41-mU"


class Logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def hook(d):
    if d['status'] == 'downloading':
        print(f'[INFO] Downloading temporary files to {d["filename"]} '
              f'at {round(d["speed"]/1000000, 2)}  MB/s', end='\r')
    if d['status'] == 'finished':
        print(f'\n[INFO] Finished downloading, converting to mp3...')

def get_download_dir():
    # read config file
    config_object = ConfigParser()
    config_object.read("conf.ini")

    # Get directory
    config = config_object["CONFIG"]
    return config["dir"]


def change_download_dir():
    dir = input("What do you want to change it to? \n")
    # '\' very bad
    dir = dir.replace("\\", '/')
    # '/' because we need it lol
    if dir[-1] != '/':
        dir = dir + '/'

    config_object = ConfigParser()
    config_object["CONFIG"] = {
        "dir": dir,
     }
    with open("conf.ini", "w") as conf:
        config_object.write(conf)

    print("You need to start YouSic again to finish saving changes")


def get_song_name(video, ydl):
    vid_name = get_video_name(video, ydl)

    if vid_name.find('-') != -1:
        return vid_name[vid_name.find('-')+2:]
    else:
        return vid_name


def get_artist(video, ydl):
    vid_name = get_video_name(video, ydl)
    # if there is a "-" in the video title, artist are usually the words
    # before it (e.g TUYU - Kakuren Bocchi)
    if vid_name.find('-') != -1:
        return vid_name[:vid_name.find('-')-1]
    # If there is not a "-", artist will be the uploader
    else:
        return ydl.extract_info(video, download=False)['uploader']


def get_video_name(video, ydl):
    vid_name = ydl.extract_info(video, download=False)['title']

    # get rid of all "/" or "\" because they are bad lol
    vid_name = vid_name.replace('\\', "_")
    vid_name = vid_name.replace("/", "_")

    return vid_name

# yoink'ed this from StackOverflow lol
def get_links_from_playlist(url):
    query = parse_qs(urlparse(url).query, keep_blank_values=True)
    playlist_id = query["list"][0]

    youtube = googleapiclient.discovery.build("youtube", "v3",
              developerKey=google_api_key)

    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()

    playlist_items = []
    while request is not None:
        response = request.execute()
        playlist_items += response["items"]
        request = youtube.playlistItems().list_next(request, response)

    return [
        f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}'
        for t in playlist_items
    ]
