import spotipy
import spotipy.util as util
import authenticator
import random
import scrobble_objects


# get scope we need to access Spotify
def get_scope():
    return 'playlist-modify-public streaming user-read-currently-playing'


# get user object to connect
def get_user_object():
    token = util.prompt_for_user_token(username=authenticator.spotify_username,
                                       scope=get_scope(),
                                       client_id=authenticator.spotify_api_key,
                                       client_secret=authenticator.spotify_api_secret,
                                       redirect_uri='https://open.spotify.com/')

    if token:
        return spotipy.Spotify(auth=token)

    return False


def get_track_artist(track):
    return track['artists'][0]['name']


def get_track_name(track):
    return track['name']


# get track uri from track object
def get_track_uri(track):
    return track['uri']


# return SpotifySong class from playlist array
def playlist_array_to_spotify_song_objects(playlist_array):
    spotify_song_objects = []
    for i, item in enumerate(playlist_array['items']):
        track = item['track']
        spotify_song_objects.append(SpotifySong(track))
    return spotify_song_objects


# class to store information currently useful on a spotify song
class SpotifySong:

    def __init__(self, spotify_track):
        self.track_artist = get_track_artist(spotify_track)
        self.track_name = get_track_name(spotify_track)
        self.spotify_uri = get_track_uri(spotify_track)

        self.check_for_unwanted_characters()

    def check_for_unwanted_characters(self):
        self.track_artist = self.track_artist.replace("…", "...")
        self.track_artist = self.track_artist.replace("’", "'")
        self.track_name = self.track_name.replace("…", "...")
        self.track_name = self.track_name.replace("’", "'")


# class for Spotify instance
class Spotify:

    def __init__(self):
        self.username = authenticator.spotify_username
        self.user = get_user_object()

    # ------------------------------------------------------------------------------------------------------------
    # best of playlist functions
    # ------------------------------------------------------------------------------------------------------------

    # get playlist id from it's name
    def get_playlist_id(self, playlist_name):
        playlists = self.user.user_playlists(self.username)
        playlist_id = ""

        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                playlist_id = playlist['id']

        return playlist_id

    # get name of the automated playlist maintained by spotytom
    def get_automated_playlist_id(self):
        return self.get_playlist_id("Automated Best Of")

    # get uri from a track name
    def get_track_uri_from_track_name(self, track):
        output = self.user.search(track, limit=1, offset=0, type='track', market=None)
        try:
            uri = get_track_uri(output["tracks"]["items"][0])

        except IndexError:
            return

        return uri

    # get songs from playlist id
    def get_songs_from_singular_playlist(self, playlist_id: int):
        new_tracks = []
        offset = 0
        finished_getting_tracks = False
        while not finished_getting_tracks:
            tracks = self.user.user_playlist_tracks(self.username,
                                                    playlist_id=playlist_id,
                                                    fields='items',
                                                    limit=100,
                                                    offset=offset)

            new_tracks.extend(playlist_array_to_spotify_song_objects(tracks))
            # not max number, so must be the end
            if len(tracks['items']) != 100:
                finished_getting_tracks = True
            else:
                offset += 100
        return new_tracks

    # get songs from all playlists from user that aren't maintained by spotytom
    def get_songs_from_playlists(self):
        new_tracks = []
        offset = 0
        finished_getting_tracks = False
        while not finished_getting_tracks:
            playlists = self.user.user_playlists(self.username, limit=50, offset=offset)

            for playlist in playlists['items']:
                if playlist['owner']['id'] == self.username and playlist['name'] != "Automated Best Of":
                    playlist_tracks = self.get_songs_from_singular_playlist(playlist['id'])
                    new_tracks.extend(playlist_tracks)

            if len(playlists['items']) != 50:
                finished_getting_tracks = True
            else:
                offset += 50

        return new_tracks

    # add tracks to automated playlist, not used as want to be able to save between uri adds
    def add_tracks(self, uri_list):
        uris = uri_list[:100]
        uri_list = uri_list[100:]
        self.user.user_playlist_add_tracks(self.username, self.get_automated_playlist_id(), uris)

        if len(uri_list) != 0:
            self.add_tracks(uri_list)

    # adds up to 100 tracks
    def add_tracks_max_100(self, uri_list):
        if len(uri_list) > 100:
            print("Error, too many uris passed, max 100")
            return

        self.add_tracks(uri_list)

    # ------------------------------------------------------------------------------------------------------------
    # explore functions
    # ------------------------------------------------------------------------------------------------------------

    def get_related_artists(self, artist_id):
        return self.user.artist_related_artists(artist_id)['artists']

    def get_random_related_artist_unique(self, artist_id, artist_array):
        related_artist = self.get_related_artists(artist_id)
        artist_count = len(related_artist)
        artist_to_return = related_artist[random.randint(0, artist_count - 1)]['uri']
        while artist_to_return in artist_array:
            artist_to_return = related_artist[random.randint(0, artist_count - 1)]['uri']
        return artist_to_return

    def get_artists_tracks(self, artist_id):
        albums = self.user.artist_albums(artist_id)
        album_uris = []
        for album in albums['items']:
            album_uris.append(album['uri'])

        track_items = []
        for album_uri in album_uris:
            track_items.extend(self.user.album_tracks(album_uri)['items'])

        track_uris = []
        for track_item in track_items:
            track_uris.append(track_item['uri'])

        return track_uris

    def get_random_artist_track(self, artist_id):
        track_uris = self.get_artists_tracks(artist_id)
        track_count = len(track_uris)
        return track_uris[random.randint(0, track_count - 1)]

    def get_artist_playing(self):
        return self.user._get("me/player/currently-playing")['item']['artists'][0]['uri']

    def get_track_playing(self):
        return self.user._get("me/player/currently-playing")['item']['uri']

    def add_tracks_to_playback(self, track_uris):
        payload = {"uris": track_uris, "offset": {"position": 0}}
        return self.user._put("me/player/play", payload=payload)
