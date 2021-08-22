import src.database as database
import src.spotify as spotify
import src.lastfm as lastfm

from . import model


class User(model.Model):

    table_name = "user"
    db_vars = ["username", "spotify_refresh_token", "lastfm_username"]

    def __init__(self):
        super().__init__()

        self.username = None
        self.spotify_access_token = None
        self.spotify_refresh_token = None
        self.lastfm_username = None

        self.default_filters = [database.DatabaseFilter("username", self.username, "=")]

        self.spotify = None
        self.lastfm = None

    @classmethod
    def create(cls):
        """ create user database, currently only designed for MySQL"""
        super().create()
        columns = None
        if type(cls.db) == database.mysql.MySQL:
            columns = [
                    database.DatabaseColumn("username", "VARCHAR(255) NOT NULL", primary=True),
                    database.DatabaseColumn("spotify_refresh_token", "VARCHAR(255)"),
                    database.DatabaseColumn("lastfm_username", "VARCHAR(255)")
            ]
        cls.db.create(cls.table_name, columns)

    @classmethod
    def load(cls, filters: list[database.DatabaseFilter] = None):
        """ load single user, rather than many """
        users = super().load(filters, 1)
        return users[0]

    def init_spotify(self):
        if self.spotify_refresh_token:
            self.spotify_access_token = spotify.authentication.refresh_token(self.spotify_refresh_token)
            self.spotify = spotify.Spotify(self.spotify_access_token)
        else:
            self.spotify = spotify.Spotify()
            token_info = self.spotify.spotipy.auth_manager.get_access_token()
            self.spotify_access_token = token_info['access_token']
            self.spotify_refresh_token = token_info['refresh_token']
            self.save()

    def init_lastfm(self):
        self.lastfm = lastfm.LastFM(self.lastfm_username)
