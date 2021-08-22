from .authentication import get_lastfm, get_lastfm_with_token


class LastFM:

    def __init__(self, username):
        self.username = username
        self.pylast = get_lastfm()
        self.pylast_user = self.pylast.get_user(self.username)
