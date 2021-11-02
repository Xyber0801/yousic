from __future__ import unicode_literals
from mutagen.easyid3 import EasyID3
import youtube_dl
import helper
from configparser import ConfigParser


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [
        {'key': 'FFmpegExtractAudio',
         'preferredcodec': 'mp3'},
        {'key': 'EmbedThumbnail'},
    ],
    'writethumbnail': True,
    'outtmpl': '{}%(title)s.%(ext)s'.format(helper.get_download_dir()),
    'prefer_ffmpeg': True,
    'keepvideo': False,
    'logger': helper.Logger(),
    'progress_hooks': [helper.hook]
}


def main():
    run = True

    while run:
        print(helper.get_download_dir())

        url = str(input(f"[PROMPT] Enter YouTube video/playlist url (type 'dir' to change download directory): "))

        if url == "dir":
            helper.change_download_dir()
            break

        # to know whether we are dealing with a playlist or a video
        if url.find('playlist?list') != -1:
            video_url = helper.get_links_from_playlist(url)
        else:
            video_url = [url]

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            for video in video_url:
                ydl.download([video])
                artist_name = helper.get_artist(video, ydl)
                song_name = helper.get_song_name(video, ydl)

                # add metadatas
                metatag = EasyID3(f'{helper.get_download_dir()}{helper.get_video_name(video, ydl)}.mp3')
                metatag['title'] = song_name
                metatag['artist'] = artist_name
                metatag.save()

                print(f'[INFO] Finished converting {helper.get_video_name(video, ydl)} to mp3!')
                print(f'[INFO]{song_name} by {artist_name} is Downloaded! \n')

        print(f'--------------------JOB DONE!--------------------')

        continue_using = input('Do you want to continue using the program? (Y/n) ')

        run = True if continue_using == 'y' or continue_using == '' else False


if __name__ == '__main__':
    main()
