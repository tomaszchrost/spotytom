from lastfm import LastFM
from spotify import Spotify
from database import Database


def format_track_name(track_name):
    return str(track_name).replace("'", "''")


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
                formatted_track = [format_track_name(track.item), int(track.weight), False]
                self.db.update_track(formatted_track)

            self.db.add_scrobble_date(date)

    def update_new_playlist_tracks(self):
        playlist_tracks = self.spotify.get_songs_from_playlists(0, [])

        for track in playlist_tracks:
            self.db.update_track_from_playlist(format_track_name(track))

    def set_songs_to_bed_added(self):
        self.db.update_to_be_added_playlist()

    def add_uris(self):
        tracks_to_add_uri = self.db.get_tracks_for_uris()
        for track in tracks_to_add_uri:
            uri = self.spotify.get_track_uri(track[0])
            if uri is not None:
                self.db.add_track_uri(track_name=format_track_name(track[0]), uri=uri)

    def add_tracks_to_playlist(self):
        tracks_to_add = self.db.get_tracks_for_playlist()
        track_uris = []

        for track in tracks_to_add:
            track_uris.append(track[4])

        if tracks_to_add:
            self.spotify.add_tracks(track_uris)

            for track in tracks_to_add:
                self.db.update_new_playlist_track(format_track_name(track[0]))
