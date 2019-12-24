import spotipy
import spotipy.util as util


def get_scope():
    return 'playlist-modify-public'


def get_user_object(username, api_key, api_secret):
    token = util.prompt_for_user_token(username=username,
                                       scope=get_scope(),
                                       client_id=api_key,
                                       client_secret=api_secret,
                                       redirect_uri='https://open.spotify.com/')

    if token:
        return spotipy.Spotify(auth=token)

    return False


def format_track_name(track):
    return track['artists'][0]['name'] + ' - ' + track['name'];


class Spotify:

    def __init__(self, username, api_key, api_secret):
        self.username = username
        self.user = get_user_object(username, api_key, api_secret)

    def get_playlist_id(self, playlist_name: str):
        playlists = self.user.user_playlists(self.username)
        playlist_id = ""

        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                playlist_id = playlist['id']

        return playlist_id

    def get_automated_playlist_id(self):
        return self.get_playlist_id("Automated Best Of")

    def get_track_uris(self, tracks: [str]):
        uris = []
        for track in tracks:
            output = self.user.search(track, limit=1, offset=0, type='track', market=None)
            try:
                uris.append(output["tracks"]["items"][0]["uri"])

            except IndexError:
                print("Error with: " + track)

        return uris

    #TODO, change == 100 to be % 100 and the list has changed from previous time
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
        self.user.user_playlist_add_tracks('temp user', self.get_automated_playlist_id(), uris)

        if len(uri_list) != 0:
            self.add_tracks(uri_list)
