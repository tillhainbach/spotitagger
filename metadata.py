from mutagen.mp4 import MP4, MP4Tags, MP4Cover, MP4FreeForm, AtomDataType
from SpotifyHelperTools import SpotifyTrackObject
import urllib.request
import os

def embed(pathToFile, music_file, Object, overwrite):
    """ Embed metadata. """
    embed = EmbedMetadata(os.path.join(pathToFile, music_file), Object, overwrite)
    if music_file.endswith('.m4a'):
        return embed.as_m4a()
    elif music_file.endswith('.mp3'):
        return embed.as_mp3()
    else:
        print('Cannot embed metadata into given output extension')
        return False

class MetadataObject:
    def __init__(self, Object):
        if isinstance(Object, SpotifyTrackObject):
            self.metadata = self._convert_from_SpotiyTrackObject(Object)
        else:
            print('cannot not convert Object')

    def _convert_from_SpotiyTrackObject(self, Object):
        Object = Object.metadata
        is_compilation = False
        if Object['album']['album_type'] == 'compilation':
            is_compilation = True
        self.metadata = {'album'        : Object['album']['name'],
                         'artist'       : ", ".join(Object['artists'][i]['name'] for i in range(len(Object['artists']))),
                         'date'         : Object['album']['release_date'],
                         'title'        : Object['name'],
                         'originaldate' : Object['album']['release_date'],
                         'comment'      : 'danceability = %.3f, energy = %.3f, valence = %.3f, instrumentalness = %.3f' % (Object['audio_features']['danceability'],
                                                             Object['audio_features']['energy'],
                                                             Object['audio_features']['valence'],
                                                             Object['audio_features']['instrumentalness']),
                         'group'        : Object['album']['label'],
                         'writer'       : '',
                         'genre'        : ', '.join(Object['genres']),
                         'tracknumber'  : [(Object['track_number'], Object['album']['total_tracks'])],
                         'albumartist'  : Object['album']['artists'][0]['name'],
                         'disknumber'   : [(Object['disc_number'],0)],
                         'cpil'         : is_compilation,
                         'albumart'     : Object['album']['images'][0]['url'], #only holds the url to albumart
                         'copyright'    : Object['album']['copyrights'][0]['text'],
                         #iTunes excepts only bpm integers. Round to prevent from being trunc by iTunes.
                         'tempo'        : [int(round(Object['audio_features']['tempo']))],
                         'lyrics'       : '',
                         'publisher'    : Object['album']['label'], #equals to label for NI Traktor
                         'audiotype'    : Object['type'], #beatport/traktor specific: track/stem/sample
                         'ISRC'         : Object['external_ids']['isrc'],
                         'PUBLISHEDDATE': Object['album']['release_date'], #Beatport release date
                         'RELEASEDATE'  : Object['album']['release_date'], #Beatport "street" date
                         'UFID'         : '', #unique Beatport identifier
                         'version'      : ', '.join(Object['versions']), #Version of the Song ("Mix")
                         'remixer'      : ', '.join(Object['remixers'][i]['name'] for i in range(len(Object['remixers']))),
                         'discription'  : Object['id']}
        return self.metadata


class EmbedMetadata(MetadataObject):
    def __init__(self, music_file, MetadataObject, overwrite):
        super().__init__(MetadataObject)
        self.music_file = music_file
        self.overwrite  = overwrite

    def _convert_to_FreeForm_string(self, tag):
        tag_in_FreeForm =  [MP4FreeForm(bytes(tag, 'utf8'), dataformat=AtomDataType.UTF8)]
        return tag_in_FreeForm

    def as_m4a(self):
        """ Embed metadata to M4A files. """
        # Apple has specific tags - see mutagen docs -
        # http://mutagen.readthedocs.io/en/latest/api/mp4.html
        tags = { 'album'        : '\xa9alb',
                 'artist'       : '\xa9ART',
                 'date'         : '\xa9day',
                 'title'        : '\xa9nam',
                 'originaldate' : 'purd',
                 'comment'      : '\xa9cmt',
                 'group'        : '\xa9grp',
                 'writer'       : '\xa9wrt',
                 'genre'        : '\xa9gen',
                 'tracknumber'  : 'trkn',
                 'albumartist'  : 'aART',
                 'disknumber'   : 'disk',
                 'cpil'         : 'cpil',
                 'albumart'     : 'covr',
                 'copyright'    : 'cprt',
                 'tempo'        : 'tmpo',
                 'lyrics'       : '\xa9lyr',
                 'publisher'    : '----:com.apple.iTunes:publisher', #equals to label for NI Traktor
                 'audiotype'    : '----:com.apple.iTunes:AUDIOTYPE', #beatport/traktor specific: track/stem/sample
                 'ISRC'         : '----:com.apple.iTunes:ISRC',
                 'PUBLISHEDDATE': '----:com.apple.iTunes:PUBLISHEDDATE', #Beatport release date
                 'RELEASEDATE'  : '----:com.apple.iTunes:RELEASEDATE', #Beatport "street" date
                 'UFID'         : '----:com.apple.iTunes:UFID', #unique Beatport identifier
                 'version'      : '----:com.apple.iTunes:VERSION', #Version of the Song ("Mix")
                 'remixer'      : '----:com.apple.iTunes:REMIXER',
                 'discription'  : 'desc'}

        audiofile = MP4(self.music_file)
        for key in self.metadata.keys():
            if self.overwrite == True or not audiofile[tags[key]]:
                #print(audiofile[tags[key]])
                if tags[key].startswith('----:com.apple.iTunes:'):
                    #use MP4FreeForm method
                    tag = self._convert_to_FreeForm_string(self.metadata[key])
                elif key == 'albumart':
                    albumart = urllib.request.urlopen(self.metadata[key])
                    tag = [MP4Cover(albumart.read(), imageformat=MP4Cover.FORMAT_JPEG)]
                    albumart.close()
                else:
                    tag = self.metadata[key]
                audiofile[tags[key]] = tag
            elif self.overwrite == 'merge' and audiofile[tags[key]]:
                if tags[key].startswith('----:com.apple.iTunes:'):
                    #use MP4FreeForm method
                    tag = self._convert_to_FreeForm_string(self.metadata[key])
                elif key == 'albumart':
                    albumart = urllib.request.urlopen(self.metadata[key])
                    tag = [MP4Cover(albumart.read(), imageformat=MP4Cover.FORMAT_JPEG)]
                    albumart.close()
                else:
                    tag = self.metadata[key]
                if not isinstance(tag, list):
                    tag = [tag]
                if not isinstance(audiofile[tags[key]], list):
                    audiofile_tag = [audiofile[tags[key]]]
                audiofile[tags[key]] = list(set().union(audiofile[tags[key]], tag))
        audiofile.save()
        return True
