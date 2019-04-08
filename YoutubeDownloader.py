import os
import shutil
import subprocess
import moviepy.editor as mp
from pytube import YouTube
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from google_images_download import google_images_download   #importing the library
from os import walk

def AddInformation(song,song_name,artist_name,album_name):
    #Add the title, artist name, and album name to the mp3 song provided
    audio = EasyID3(song)
    audio['title'] = u"{}".format(song_name)
    audio['artist'] = u"{}".format(artist_name)
    audio['album'] = u"{}".format(album_name)
    audio.save()

def AddCoverArt(song,art):
    #Add cover art to the mp3 file provided
    audio = MP3(song, ID3=ID3)

    # add ID3 tag if it doesn't exist
    try:
        audio.add_tags()
    except error:
        pass

    audio.tags.add(
        APIC(
            encoding=3, # 3 is for utf-8
            mime='image/png', # image/jpeg or image/png
            type=3, # 3 is for the cover image
            desc=u'Cover',
            data=open(art, 'rb').read()
        )
    )
    audio.save()

def FindAndAddCoverArt(artist_name, album_name):
    #Set up the keywords which you will search to find the album cover on the internet
    my_keywords = artist_name + " "+ album_name + " Album cover"

    response = google_images_download.googleimagesdownload()   #class instantiation

    #Download the first image that appears on google to a folder labeled the same as the keywords
    arguments = {"keywords": my_keywords , "limit":1,"print_urls" : True, "output_directory": '/Users/arashdehghan/Desktop/YouTube Downloader/'""}   #creating list of arguments
    paths = response.download(arguments)   #passing the arguments to the function
    #print(paths)   #printing absolute paths of the downloaded images

    #Grab the name and location of the photo
    mypath = '/Users/arashdehghan/Desktop/YouTube Downloader/'+my_keywords
    f = []
    for (dirpath, dirnames, filenames) in walk(mypath):
        f.extend(filenames)
        break
    my_photo = mypath+'/'+f[0]

    #Return both the path to the photo, as well as the path to the file which holds the photo
    return my_photo,mypath

def SaveYouTubeAsVideo(link,location, artist_name, album_name):
    try:
        #Create a new name for the file
        new_name = artist_name + " - " + album_name

        #Download the YouTube video from YT
        YouTube(link).streams.first().download(location)

        #Grab the original title of the YT video
        og_video_name = YouTube(link).title
        #Take out ',",/,\ from the original title name
        og_video_name = og_video_name.replace("'","")
        og_video_name = og_video_name.replace('"','')
        og_video_name = og_video_name.replace('/','')
        og_video_name = og_video_name.replace('\\','')

        #Rename the downloaded video to our new specified name
        os.rename(location+og_video_name+""".mp4""", location+new_name+""".mp4""")
    except:
        print("Error. Please double check that you have provided the necessary information")


def SaveYouTubeAsAudio(link,location,artist_name, album_name, song_name, song_cover = None):
    try:
        #Create a new name for the file
        new_name = song_name + " - " + artist_name

        #Download the YouTube video from YT
        YouTube(link).streams.first().download(location)
        #Can also download only the audio using the following, but this surprisingly takes longer
        ### YouTube(link).streams.filter(only_audio=True).first().download(location)
        #Also can download a lower quality video, since we are deleting the video regardless, which should reduce the download time somewhat (Code example below). But we will just stick with what we have for now
        ### YouTube(link).streams.filter(res = '144p').first().download(location)

        #Grab the original title of the YT video
        og_video_name = YouTube(link).title
        #Take out ',",/,\ from the original title name
        og_video_name = og_video_name.replace("'","")
        og_video_name = og_video_name.replace('"','')
        og_video_name = og_video_name.replace('/','')
        og_video_name = og_video_name.replace('\\','')

        #Convert the video file to an audio file
        clip = mp.VideoFileClip(location+og_video_name+""".mp4""")
        clip.audio.write_audiofile(location+new_name+""".mp3""")
        #Delete the video file
        os.remove(location+og_video_name+""".mp4""")

        #Add information to the audio file, such as the song name, artist name, and album name
        AddInformation(location+new_name+""".mp3""",song_name,artist_name,album_name)

        #Add also some cover art/album art. If the user provided their own album art, apply it to the mp3 file.
        if song_cover != None:
            AddCoverArt(location+new_name+""".mp3""",song_cover)
        #If they haven't included an image, then we will search the internet to find them a cover photo and add it to the mp3 for them
        else:
            found_cover, path_to_del = FindAndAddCoverArt(artist_name,album_name)
            AddCoverArt(location+new_name+""".mp3""",found_cover)
            os.remove(found_cover)
            os.rmdir(path_to_del)

        #Move the mp3 from our original location to iTunes, where it will be automatically added to your library
        shutil.move(location+new_name+".mp3", "/Users/arashdehghan/Music/iTunes/iTunes Media/Automatically Add to iTunes.localized/"+new_name+".mp3")

    except:
        print("Error. Please double check that you have provided the necessary information")



################################################################################

# An example using John Mayers' performance on Instagram Live of his unreleased song 'Blue Skies at Night'
my_link = """https://www.youtube.com/watch?v=SYJTIGRnAzw"""
my_path = """"""

artist_name = "John Mayer"
album_name = "Live Performances"
song_name = "Blue Skies"
song_cover = "continuum.jpg" #If you would rather choose a specific cover, download it yourself and paste the path to it below and then include it in the SaveYouTubeAsAudio
################################################################################

SaveYouTubeAsAudio(my_link , my_path, artist_name, album_name, song_name)
