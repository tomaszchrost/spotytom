from src.spotify import Spotify
from src.database import Database
from src import scrobble_objects
import MySQLdb
from src.scrobble_object_utils import string_equal
import logging


# error when db returns multiple tracks of the name, shouldn't ever happen
class UniqueIndexException(Exception):
    """Raised when more than one of a unique index found"""
    pass


# uses other implemented tasks for carry out processes
class ProcessLastTracksOfAlbum:

    # initialise other classes
    def __init__(self, spotify_token=None, flask_username=None):
        self.spotify = Spotify(spotify_token)
        self.db = Database(flask_username)
        self.ScrobbleData = self.db.get_scrobble_tracks()

    # searches last fm for new tracks and updates scrobble data
    def add_last_tracks_of_album(self):
        tracks_in_playlist = [track.spotify_uri for track in self.ScrobbleData if track.in_playlist]

        low_index = 0

        spotify_tracks = []
        while low_index < len(tracks_in_playlist):
            high_index = min(len(tracks_in_playlist), low_index + 50)

            songs_for_request = tracks_in_playlist[low_index:high_index]

            spotify_tracks.append(self.spotify.user.tracks(songs_for_request))
            low_index = high_index

        add_to_playlist = []
        for spotify_results in spotify_tracks:
            for spotify_track in spotify_results['tracks']:
                tracks_in_album = spotify_track['album']['total_tracks']
                track_number = spotify_track['track_number']
                if tracks_in_album == track_number and tracks_in_album > 6:
                    add_to_playlist.append(spotify_track['uri'])

        playlist_id = self.spotify.get_playlist_id('Last Tracks')
        low_index = 0

        while low_index < len(add_to_playlist):
            high_index = min(len(tracks_in_playlist), low_index + 100)
            self.spotify.add_tracks_max_100(add_to_playlist[low_index:high_index], playlist_id)
            low_index = high_index