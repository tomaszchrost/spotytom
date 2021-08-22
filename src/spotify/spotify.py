from src import spotify

import authenticator


class Spotify:

    def __init__(self, token=None):
        if token:
            self.spotipy = spotify.authentication.get_user_with_token(token)
        else:
            self.spotipy = spotify.authentication.get_user_object()

        self.username = self.spotipy.me()['id']
