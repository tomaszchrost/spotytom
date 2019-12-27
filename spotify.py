import spotipy
import spotipy.util as util
import communicator
import authenticator
import random


def get_scope():
    return 'playlist-modify-public streaming user-read-currently-playing'


def get_user_object():
    token = util.prompt_for_user_token(username=authenticator.spotify_username,
                                       scope=get_scope(),
                                       client_id=authenticator.spotify_api_key,
                                       client_secret=authenticator.spotify_api_secret,
                                       redirect_uri='https://open.spotify.com/')

    if token:
        return spotipy.Spotify(auth=token)

    return False


def format_track_name(track):
    return track['artists'][0]['name'] + ' - ' + track['name']


class Spotify:

    def __init__(self):
        self.username = authenticator.spotify_username
        self.user = get_user_object()

    def get_playlist_id(self, playlist_name):
        playlists = self.user.user_playlists(self.username)
        playlist_id = ""

        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                playlist_id = playlist['id']

        return playlist_id

    def get_automated_playlist_id(self):
        return self.get_playlist_id("Automated Best Of")

    def get_track_uri(self, track):
        uri = ""
        output = self.user.search(track, limit=1, offset=0, type='track', market=None)
        try:
            uri = output["tracks"]["items"][0]["uri"]

        except IndexError:
            return

        # communicator.output_uri_find(track)
        return uri

    def get_track_uris(self, tracks):
        uris = []
        for track in tracks:
            output = self.user.search(track, limit=1, offset=0, type='track', market=None)
            try:
                uris.append(output["tracks"]["items"][0]["uri"])

            except IndexError:
                print("Error with: " + track)

        return uris

    def get_songs_from_singular_playlist(self, playlist_id: int, offset: int, new_tracks: [str]):
        tracks = self.user.user_playlist_tracks(self.username,
                                                playlist_id=playlist_id,
                                                fields='items',
                                                limit=100,
                                                offset=offset)

        for i, item in enumerate(tracks['items']):
            track = item['track']
            new_tracks.append(format_track_name(track))

        if len(tracks['items']) == 100:
            self.get_songs_from_singular_playlist(playlist_id, offset + 100, new_tracks)

        return new_tracks

    def get_songs_from_playlists(self, offset: int, new_tracks: [str]):
        playlists = self.user.user_playlists(self.username, limit=50, offset=offset)

        for playlist in playlists['items']:
            if playlist['owner']['id'] == self.username and playlist['name'] != "Automated Best Of":
                playlist_tracks = self.get_songs_from_singular_playlist(playlist['id'], 0, [])
                new_tracks.extend(playlist_tracks)

        if len(playlists['items']) == 50:
            self.get_songs_from_playlists(offset + 50, new_tracks)

        return new_tracks

    def add_tracks(self, uri_list):
        uris = uri_list[:100]
        uri_list = uri_list[100:]
        self.user.user_playlist_add_tracks(self.username, self.get_automated_playlist_id(), uris)

        if len(uri_list) != 0:
            self.add_tracks(uri_list)

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




