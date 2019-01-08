from SpotifyHelperTools import SpotifyHelperTools
from iTunesHelperTools import iTunesHelperTools
import argparse

def iTunesPlaylistToSpotify(inputxml):
    iTunes = iTunesHelperTools()
    iTunesPlaylist = iTunes.getiTunesPlaylist(args.input)
    playlistName = iTunes.getiTunesPlaylistName(iTunesPlaylist)
    spotifyTrackIDs = iTunes.getSpotifyTrackIDsfromiTunesPlaylist(iTunesPlaylist)
    SpotifyUser = SpotifyHelperTools()
    SpotifyUser.main(playlistName, spotifyTrackIDs)

if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('-i', '--input', help = 'xml file of iTunes Playlist')
    args = a.parse_args()
    iTunesPlaylistToSpotify(args.input)
