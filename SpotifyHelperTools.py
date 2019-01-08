# parts of this code is copied from http://www.tomcasavant.com/?p=64
import spotipy
import spotipy.util as util
from configparser import SafeConfigParser
import re
import weakref
import json

#helper functions
def compare_strings(string1, string2):
    translations_1 = {'ä':'a', 'å':'a', 'æ':'a',
                    'Ä':'A', 'Å':'A', 'Æ':'A',
                    'ö':'o', 'ø':'o', 'œ':'o',
                    'Ö':'O', 'Ø':'O', 'Œ':'O',
                    'ü':'u', 'Ü':'U'}
    translations_2 = {'ä':'ae', 'å':'a', 'æ':'ae',
                    'Ä':'Ae', 'Å':'A', 'Æ':'Ae',
                    'ö':'oe', 'ø':'o', 'œ':'oe',
                    'Ö':'Oe', 'Ø':'O', 'Œ':'Oe',
                    'ü':'ue', 'Ü':'Ue'}
    if string1 in string2:
       return True
    else:
       for char in translations_1:
          string1 = string1.replace(char, translations_1[char])
          string2 = string2.replace(char, translations_1[char])
       if string1 in string2:
          return True
       else:
          for char in translations_2:
              string1 = string1.replace(char, translations_2[char])
              string2 = string2.replace(char, translations_2[char])
          if string1 in string2:
              return True
          else:
              return False

def find_in_listed_dict(lst, key, value):
    for i, dic in enumerate(lst):
        if compare_strings(string1 = dic[key], string2 = value):
            return i
    return None

def nice_print(Object, **kwargs):
    print(json.dumps(Object, indent = 2))

class SpotifyHelperTools:
    _instances = set()

    @classmethod
    def getinstances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    def __init__(self, username = None):
        parser = SafeConfigParser() #Reads config.ini file for API keys
        parser.read('config.ini')
        self.CLIENT_ID = parser.get('spotify', 'CLIENT_ID')
        self.CLIENT_SECRET = parser.get('spotify', 'CLIENT_SECRET')
        #self.REDIRECT_URI = parser.get('spotify', 'REDIRECT_URI')
        #Allows program to access/edit private and public playslist
        self.SCOPE = "playlist-read-private playlist-modify-private playlist-read-collaborative playlist-modify-public"
        self.username = username
        self.sp = self.getUser() # Creates Spotify Instance
        self.id = self.sp.me()['id'] # Gets ID of authenticating user
        self._instances.add(weakref.ref(self)) #keeps track of runnning instances

    def getUser(self):
        """ Creates Spotify instance for Authenticating User """
        token = self.getUserToken()
        sp = spotipy.Spotify(auth = token)
        sp.trace = False
        return sp

    def getUserToken(self):
        """ Gets authentication token from user"""
        username = self.username
        if not username:
            username = input("Please enter your Spotify username: ")
        token = util.prompt_for_user_token(username = username, scope = self.SCOPE, client_id = self.CLIENT_ID, client_secret = self.CLIENT_SECRET)#, redirect_uri = self.REDIRECT_URI)
        return token

    def createPlaylist(self, title, tracks):
        """Creates a new playlist containing all tracks"""
        playlist = self.sp.user_playlist_create(self.id, title, public = False)
        max_number_query_items = 100
        if len(tracks) > max_number_query_items:
            repeat = int(len(tracks) / max_number_query_items) + 1
            for i in range(repeat):
                self.sp.user_playlist_add_tracks(self.id, playlist['id'], tracks[max_number_query_items * i : max_number_query_items  + max_number_query_items * i])
        else:
            self.sp.user_playlist_add_tracks(self.id, playlist['id'], tracks)
        print ("Playlist \"" + title + "\" created")

    def fetch_playlist(self, playlist):
        # if not fields:
        #     fields = 'tracks.items(track(!preview_url, available_markets, external_urls, href)), tracks.items(track(album(!artists, external_urls, href, available_markets)))'
        result = self.sp.playlist(playlist)

        return result

    def get_tracks_genres(self, ListofSpotifyTrackObjects):
        ids = []
        artists = []
        genres = []
        if not isinstance(ListofSpotifyTrackObjects, list):
            ListofSpotifyTrackObjects = [ListofSpotifyTrackObjects]
        for i, SpotifyTrackObject in enumerate(ListofSpotifyTrackObjects):
            while True:
                try:
                    id = (SpotifyTrackObject.metadata['remixers'])
                    if not id[0]:
                        ids.append(SpotifyTrackObject.metadata['artists'][0]['id'])
                    elif not id[0]['id']:
                        ids.append(SpotifyTrackObject.metadata['artists'][0]['id'])
                    else:
                        ids.append(id[0]['id'])
                    break
                except KeyError:
                    SpotifyTrackObject.remixers()
                    print('remixer not in track metatada. Trying to identify remixer first')
                    continue
                else:
                    break
            #print('%s : %s' % (SpotifyTrackObject._name, ids[i]))
        max_number_query_items = 50
        if len(ids) > max_number_query_items:
            repeat = int(len(ids) / max_number_query_items) + 1
            for i in range(repeat):
                artists += self.sp.artists(ids[max_number_query_items * i : max_number_query_items + max_number_query_items * i])['artists']
        else:
            # names = [track._name for track in ListofSpotifyTrackObjects]
            # id_name_dict = dict(zip(names, ids))
            # nice_print(id_name_dict)
            artists += self.sp.artists(ids)['artists']
        for artist, SpotifyTrackObject in zip(artists,ListofSpotifyTrackObjects):
            genres.append(artist['genres'])
            SpotifyTrackObject.metadata['genres'] = artist['genres']
        return genres

    def get_audio_features(self, ListofSpotifyTrackObjects):
        ids = []
        audio_features = []
        #prevent from failing if only a single unlisted SpotifyTrackObject is passed
        if not isinstance(ListofSpotifyTrackObjects, list):
            ListofSpotifyTrackObjects = [ListofSpotifyTrackObjects]
        for SpotifyTrackObject in ListofSpotifyTrackObjects:
            ids.append(SpotifyTrackObject.metadata['id'])
        max_number_query_items = 100
        if len(ids) > max_number_query_items:
            repeat = int(len(ids) / max_number_query_items) + 1
            for i in range(repeat):
                audio_featuress += self.sp.audio_features(ids[max_number_query_items * i : max_number_query_items + max_number_query_items * i])
        else:
            # print(ids)
            audio_features += self.sp.audio_features(ids)
            # nice_print (audio_features)
            # audio_features = audio_features
        for audio_feature, SpotifyTrackObject in zip(audio_features, ListofSpotifyTrackObjects):
            SpotifyTrackObject.metadata['audio_features'] = audio_feature
        return audio_features

    def get_additional_album_info(self, ListofSpotifyTrackObjects):
        ids = []
        albums = []
        if not isinstance(ListofSpotifyTrackObjects, list):
            ListofSpotifyTrackObjects = [ListofSpotifyTrackObjects]
        for SpotifyTrackObject in ListofSpotifyTrackObjects:
            ids.append(SpotifyTrackObject.metadata['album']['id'])
        max_number_query_items = 20
        if len(ids) > max_number_query_items:
            repeat = int(len(ids) / max_number_query_items) + 1
            for i in range(repeat):
                albums += self.sp.albums(ids[max_number_query_items * i : max_number_query_items + max_number_query_items * i])['albums']
        else:
            albums += self.sp.albums(ids)['albums']
        for album, SpotifyTrackObject in zip(albums, ListofSpotifyTrackObjects):
            del album ['tracks']
            SpotifyTrackObject.metadata['album'] = {**SpotifyTrackObject.metadata['album'], **album}
        return SpotifyTrackObject.metadata['album']

    def _remixer_search(self, SpotifyTrackObject, remixer):
        #Remixer is not listed as artist. Search on Spotify for artist
        try:
            artist = self.sp.search(remixer, limit = 1, type = 'artist')['artists']['items'][0]
        except IndexError:
            try:
                remixer = remixer.split("'", 1)[0]
                search = spotify.search(remixer, limit = 5, type = 'artist')['artists']['items']
                artist = sorted(search, key=itemgetter('popularity'), reverse=True)[0]
            except IndexError:
                print('Remixer %s not found on Spotify' % (remixer))
                return False
        SpotifyTrackObject.metadata['artists'].append(artist)

    def complete_tracks_tags(self, ListofSpotifyTrackObjects):
        #prevent from failing if only a single unlisted SpotifyTrackObject is passed
        if not isinstance(ListofSpotifyTrackObjects, list):
            ListofSpotifyTrackObjects = [ListofSpotifyTrackObjects]
        for SpotifyTrackObject in ListofSpotifyTrackObjects:
            SpotifyTrackObject.versions()
            SpotifyTrackObject.remixers()
        self.get_audio_features(ListofSpotifyTrackObjects)
        self.get_additional_album_info(ListofSpotifyTrackObjects)
        self.get_tracks_genres(ListofSpotifyTrackObjects)

    def main(self, playlistName, spotifyTrackIDs):
        self.createPlaylist(playlistName, spotifyTrackIDs)

class SpotifyTrackObject:
    def __init__(self, metadata):
        self.metadata = metadata
        self._name = metadata['name']

    def _set_versions(self):
        '''looks for the version keywords in the trackname and returns the version
        of a track. eg. "Sample Name (Orginal Mix)" returns ['Orginal Mix']'''
        versiontypes = ['Mix','Edit','Remix','Version','Rework', 'Dub']
        versiontype_prefixes= {'Disco', '12"', 'Radio', 'Original', 'Orig.', 'Club',
                                'VIP', 'Acoustic', 'Instrumental', 'Single',
                                'DJ','Video', 'Party', 'Main', 'Dub',
                                'Extended','12" Enxtended','12" Extended Disco',
                                'Us', 'USA', 'USA European Connection',''}
        keywords = (prefix + ' ' + versiontype for versiontype in versiontypes for prefix in versiontype_prefixes)
        version = [word for word in keywords if word in  self._name]
        to_remove = [x for x in version for y in version if x != y and x in y]
        self.metadata ['versions'] = [x.lstrip() for x in version if x not in to_remove]
        return self.metadata ['versions']

    def versions(self):
        try:
            return self.metadata ['versions']
        except KeyError:
            return self._set_versions()

    def _remixer_index_in_ArtistObject(self, remixer):
        return find_in_listed_dict(self.metadata['artists'], 'name', remixer)

    def remixers(self):
        try:
            return self.metadata['remixers']
        except KeyError:
            return self._set_remixers()

    def _set_remixers(self):
        versions = self.versions()
        if not versions:
            self.metadata ['remixers'] = [{'name':'', 'index': '', 'id':''}]
            #print('The track "%s" has no remixers' % self._name)
            return
        '''looks for the version keywords in the trackname and returns the remixers.
        Usually, it is enclosed in (), [] or after -
        eg. Sample Name - Remixerfirst RemixerLast Remix (Editorfirst EditorLast Edit),
        will return ['Remixerfirst RemixerLast', 'Editorfirst EditorLast']'''
        remixers = []
        for version in versions:
            findseperator = '(?<=%s)\W' % version
            versionseperator = re.search(findseperator, self._name)
            if not versionseperator or versionseperator.group(0) in [' ', ',']:
                versionseperator = '\W\s'
            elif versionseperator.group(0) == ']':
                versionseperator = '\['
            elif versionseperator.group(0) == ')':
                versionseperator = '\('
            search_string = '(?<=%s)[\'\"\w\s]*(?= %s)' % (versionseperator, version)
            try:
                remixers.append(re.findall(search_string, self._name)[-0].lstrip())
            except IndexError:
                pass
        if not remixers:
            self.metadata ['remixers'] = [{'name':'', 'index': '', 'id':''}]
            #print('The track "%s" has no remixers' % self._name)
            return
        ids = []
        indexes = []
        for remixer in remixers:
            i = find_in_listed_dict(self.metadata['artists'], 'name', remixer)
            if not i:
                next(SpotifyHelperTools.getinstances())._remixer_search(self, remixer)
                i = find_in_listed_dict(self.metadata['artists'], 'name', remixer)
                if not i:
                    ids.append(i)
                else:
                    ids.append(self.metadata['artists'][i]['id'])
            else:
                ids.append(self.metadata['artists'][i]['id'])
            indexes.append(i)
        self.metadata ['remixers'] = [{'name':item[0], 'index': item [1], 'id':item[2]} for item in zip(remixers, indexes, ids)]
        return self.metadata ['remixers']

    def complete_tags(self):
        self.versions()
        self.remixers()
        next(SpotifyHelperTools.getinstances()).get_audio_features(self)
        next(SpotifyHelperTools.getinstances()).get_additional_album_info(self.metadata['album'])
        next(SpotifyHelperTools.getinstances()).get_tracks_genres(self)
