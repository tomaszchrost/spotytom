from src.spotify import Spotify
from src.database import Database
from src import scrobble_objects
import logging

play_count_to_be_removed = 5
# used for skipping over issues, if I just need it to work
hide_errors = False


# uses other implemented tasks for carry out processes
class ProcessDeleteFromPlaylist:

    playlist_name = 'Automated Discover'

    # initialise other classes
    def __init__(self, spotify_token=None, flask_username=None):
        self.spotify = Spotify(spotify_token)
        self.db = Database(flask_username)
        self.ScrobbleData = self.db.get_scrobble_tracks()

    def delete_from_playlist(self):
        playlist_id = self.spotify.get_playlist_id(self.playlist_name)
        if not playlist_id:
            return
        playlist_tracks = self.spotify.get_songs_from_singular_playlist(playlist_id)
        uris_to_remove = []
        for track in playlist_tracks:
            for scrobble_track in self.ScrobbleData:
                if track.track_artist == scrobble_track.track_artist and track.track_name == scrobble_track.track_name:
                    if scrobble_track.play_count >= play_count_to_be_removed:
                        uris_to_remove.append(scrobble_track.spotify_uri)
                        print(f"{track.track_artist} {track.track_name} to be deleted")
                    else:
                        print(f"{track.track_artist} {track.track_name} not to be deleted")
                    break
        self.spotify.user.user_playlist_remove_all_occurrences_of_tracks(playlist_id, uris_to_remove)
