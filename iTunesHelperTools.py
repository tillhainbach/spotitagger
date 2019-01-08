import plistlib
from urllib.parse import unquote
from mutagen.mp4 import MP4
from mutagen.easyid3 import EasyID3

class iTunesHelperTools:
    def __init__(self):
        self.name = "IAmAHappyHelper"

    def getiTunesPlaylistName(self, iTunesPlaylist):
        playlistName = iTunesPlaylist['Playlists'][0]['Name']
        return playlistName

    def getiTunesPlaylist(self, file):
        with open(file, 'rb') as fp:
            iTunesPlaylist = plistlib.load(fp)
        return iTunesPlaylist

    def getSpotifyTrackIDfromFile(self, music_file):
        if music_file.endswith('.mp3'):
            spotifyTrackID = EasyID3(music_file)['version'][0]
        elif music_file.endswith('.m4a'):
            spotifyTrackID = MP4(music_file)['desc'][0]
        return spotifyTrackID

    def getSpotifyTrackIDsfromiTunesPlaylist(self, iTunesPlaylist):
        spotifyTrackIDs = []
        for track_id, track_info in iTunesPlaylist['Tracks'].items():
            music_file = unquote(track_info['Location'][7:])
            spotifyTrackIDs.append(self.getSpotifyTrackIDfromFile(music_file))
        return spotifyTrackIDs
