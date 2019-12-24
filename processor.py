from .lastfm import LastFM
from .spotify import Spotify
from .database import Database

class Processor:

    def __init__(self):
        self.lastfm = LastFM()
        self.spotify = Spotify()
        self.db = Database()
