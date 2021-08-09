from src.spotify import Spotify
from src.database import Database
from src import scrobble_objects
from src.scrobble_object_utils import string_equal

hide_errors = False


# TODO standardise print outputs to stdout
# error when db returns multiple tracks of the name, shouldn't ever happen
class UniqueIndexException(Exception):
    """Raised when more than one of a unique index found"""
    pass


# uses other implemented tasks for carry out processes
class ProcessAddPlaylist:

    # initialise other classes
    def __init__(self, playlist_id, spotify_token=None, flask_username=None):
        print("PLAYLIST ID: " + playlist_id)
        self.spotify = Spotify(spotify_token)
        self.db = Database(flask_username)
        self.ScrobbleData = self.db.get_scrobble_tracks()
        self.playlist_id = playlist_id

    def add_playlist_tracks(self):
        spotify_tracks = self.spotify.get_songs_from_singular_playlist(self.playlist_id)
        for spot_track in spotify_tracks:
            matching_tracks = [x
                for x in self.ScrobbleData
                if string_equal(x.track_name, spot_track.track_name)
                and string_equal(x.track_artist, spot_track.track_artist)]
            try:
                # make sure it's set to be added if not already in playlist, and update uri while available
                if len(matching_tracks) == 1:
                    matching_track = matching_tracks[0]
                    if not matching_track.in_playlist and not matching_track.to_be_added:
                        matching_track.to_be_added = True
                        matching_track.spotify_uri = spot_track.spotify_uri
                        matching_track.save(self.db)
                        print(
                            matching_track.track_artist + " - " + matching_track.track_name + " set to be added to playlist")
                # add new track, already to be added to playlist and update uri while available
                elif len(matching_tracks) == 0:
                    new_scrobble_track = scrobble_objects.ScrobbleTrack(
                        track_artist=spot_track.track_artist,
                        track_name=spot_track.track_name,
                        to_be_added=True,
                        spotify_uri=spot_track.spotify_uri)
                    self.ScrobbleData.append(new_scrobble_track)
                    new_scrobble_track.save(self.db)
                    print("Added new track " + new_scrobble_track.track_artist + " - " + new_scrobble_track.track_name)

                else:
                    raise UniqueIndexException

            except UniqueIndexException:
                print("Two matching tracks found, unique index error!")
