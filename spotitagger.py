import timeit
from SpotifyHelperTools import SpotifyHelperTools, SpotifyTrackObject
import json
import os
import metadata
import handle
import const
import pprint
import platform
import sys

def list_all_m4a_files(path):
    '''return a generator object for all .m4a-files in the directory "path".
    Only audiofile in M4A-format are support by this script at the moment.'''
    for file in os.listdir(path):
        if file.endswith('.m4a'):
            yield file

def get_music_file_metadata(song):
    '''Returns the artist name and song title from the audiofile name.
    the audiofile should be in the format:
                    "songname %-% songartist.m4a"
    so the song title can be clearly distinguished from the artist name.
    Spotify also uses " - " in song titles eg. when it is a remix.'''
    filetitle, fileartist = song.split(" %-% ")
    fileartist = fileartist[:-4]
    return (filetitle, fileartist)

def find_music_files_in_playlist(playlist_tracklist, audiofiles):
    '''for every audiofile return its index (e.g. position) in the spotify playlist.
    returns a list of indexes'''
    idx = []
    for file in audiofiles:
        filetitle, fileartist = get_music_file_metadata(file)
        for i, dict in enumerate(playlist_tracklist):
            if filetitle == dict['track']['name']:
                artists = []
                for artist in dict['track']['artists']:
                    artists.append(artist['name'])
                artists = ', '.join(artists)
                if set (fileartist) == set(artists):
                    idx.append(i)
    return idx

def nice_print(Object):
    '''a wrapper for neat printing of JSON-like objects'''
    print(json.dumps(Object, indent = 2))

def benchmark (func, *args, **kwargs):
    '''show how long it took.'''
    start_time = timeit.default_timer()
    func(*args, **kwargs)
    elapsed_time = timeit.default_timer() - start_time
    print ('%s took %.5f seconds' % (func.__name__,elapsed_time))

def main_playlist(uri, path, audiofiles):
    '''main function, looks up all audio files in path in playlist uri and embeds
    the metadata taken from spotify web api into the respective audio file.'''
    sp = SpotifyHelperTools(const.args.username)
    result = sp.sp.playlist(uri, fields = 'tracks.items')['tracks']['items']
    if not result:
        # abort if an empty spotify playlist was provided
        log.warning('empty Spotify playlist. Exiting program')
        return
    music_files = {audiofile : index for audiofile, index in zip(audiofiles, find_music_files_in_playlist(result, audiofiles)) if index}
    if not music_files:
        # abort if none of the audiofiles are in the spotify playlist
        log.warning('None of the audiofiles are in the spotify playlist.')
        return
    tracks = {file : SpotifyTrackObject(result[i]['track']) for file, i in music_files.items()}
    sp.complete_tracks_tags(list(tracks.values()))
    for music_file, track in tracks.items():
        metadata.embed(path, music_file, track, overwrite = const.args.overwrite)

if __name__ == '__main__':
    # get arguments/default arguments
    const.args = handle.get_arguments()
    # setup logger/log file
    log = const.logzero.setup_logger(formatter=const.formatter,
                                      level=const.args.log_level, logfile = const.log_file)
    log.debug('Python version: {}'.format(sys.version))
    log.debug('Platform: {}'.format(platform.platform()))
    log.debug(pprint.pformat(const.args.__dict__))

    try:
        # get all audiofiles in directory first and check whether there are any.
        # abort if none.
        audiofiles = list(list_all_m4a_files(const.args.folder))
        if not audiofiles:
            log.warning('No .m4a files in directory. This program only supports audiofiles in M4A-Format. Exiting program')
            sys.exit(0)

        if const.args.playlist:
            benchmark(main_playlist, const.args.playlist, const.args.folder, audiofiles)

        # actually we don't necessarily need this, but yeah...
        # explicit is better than implicit!
        sys.exit(0)

    except KeyboardInterrupt as e:
        log.exception(e)
        sys.exit(3)
