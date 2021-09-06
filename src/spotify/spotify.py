import spotipy
import authenticator
import random
import src.spotify.authentication as spotify_authentication
import logging


def get_track_artist(track):
    return track['artists'][0]['name'].lower()


def get_track_name(track):
    return track['name'].lower()


# get track uri from track object
def get_track_uri(track):
    return track['uri']


# return SpotifySong class from playlist array
def playlist_array_to_spotify_song_objects(playlist_array):
    spotify_song_objects = []
    for i, item in enumerate(playlist_array['items']):
        track = item['track']
        if track:
            spotify_song_objects.append(SpotifySong(track))
    return spotify_song_objects


# class to store information currently useful on a spotify song
class SpotifySong:

    def __init__(self, spotify_track):
        self.track_artist = get_track_artist(spotify_track)
        self.track_name = get_track_name(spotify_track)
        self.spotify_uri = get_track_uri(spotify_track)


# class for Spotify instance
class Spotify:

    def __init__(self, token=None):
        if token:
            self.user = spotify_authentication.get_user_with_token(token)
            self.username = self.user.me()['id']
        else:
            self.username = authenticator.spotify_username
            self.user = spotify_authentication.get_user_object()

    # ------------------------------------------------------------------------------------------------------------
    # best of playlist functions
    # ------------------------------------------------------------------------------------------------------------

    # get playlist id from it's name
    def get_playlist_id(self, playlist_name):
        playlists = self.user.current_user_playlists(limit=None)
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
    def add_tracks(self, uri_list, playlist_id=None):
        # TODO dirty code, should be specified by web_row
        if playlist_id is None:
            playlist_id = self.get_automated_playlist_id()

        uris = uri_list[:100]
        uri_list = uri_list[100:]
        # handle local uris
        if uris:
            uris = [uri for uri in uris if uri is not None and "spotify:local" not in uri]
            self.user.user_playlist_add_tracks(self.username, playlist_id, uris)

        if uri_list:
            self.add_tracks(uri_list, playlist_id=playlist_id)

    # adds up to 100 tracks
    def add_tracks_max_100(self, uri_list, playlist_id=None):
        if len(uri_list) > 100:
            logging.info("Error, too many uris passed, max 100")
            return

        self.add_tracks(uri_list, playlist_id=playlist_id)

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
        return self.user.current_user_playing_track()['item']['artists'][0]['uri']

    def get_track_playing(self):
        return self.user.current_user_playing_track()['item']['uri']

    def add_tracks_to_playback(self, track_uris):
        for uri in track_uris:
            self.user.add_to_queue(uri)
