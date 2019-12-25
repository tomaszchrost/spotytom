from .lastfm import LastFM
from .spotify import Spotify
from .database import Database

class Processor:

    def __init__(self):
        self.lastfm = LastFM()
        self.spotify = Spotify()
        self.db = Database()

    def update_new_tracks(self):
        lastfm_dates = self.lastfm.get_scrobble_dates()
        db_dates = self.db.get_scrobble_dates()

        new_dates = list(set(lastfm_dates) - set(db_dates))

        for date in new_dates:
            new_tracks = self.lastfm.get_scrobbles(date[0], date[1])
            for track in new_tracks:
                self.db.update_track(track)

        self.db.add_scrobble_dates()

    def add_tracks_to_playlist(self):
        tracks_to_add = self.db.get_tracks_for_playlist()
        track_uris = self.spotify.get_track_uris(tracks_to_add)
        self.spotify.add_tracks(track_uris)

        for track in tracks_to_add:
            self.db.update_new_playlist_track(track)
            

