from src.spotify import Spotify
from src.database import  Database
import random


# uses other implemented tasks for carry out processes
class ProcessSmartShuffle:

    # initialise other classes
    def __init__(self, spotify_token=None, flask_username=None):
        self.spotify = Spotify(spotify_token)
        self.db = Database(flask_username)
        self.ScrobbleData = self.db.get_scrobble_tracks()

    def reset_shuffles(self):
        for track in self.ScrobbleData:
            track.shuffled = False
            self.db.save_scrobble_track()

    def get_shuffle_tracks(self):
        shuffle_tracks = []
        for db_track in self.ScrobbleData:
            if not db_track.shuffled and db_track.in_playlist:
                shuffle_tracks.append(db_track)
        return shuffle_tracks

    def start_smart_shuffle(self):
        shuffle_tracks = self.get_shuffle_tracks()
        if len(shuffle_tracks) == 0:
            self.reset_shuffles()
            shuffle_tracks = self.get_shuffle_tracks()

        random.shuffle(shuffle_tracks)
        queue_tracks = shuffle_tracks[:100]

        for track in queue_tracks:
            print(f"Adding track {track.track_name}")
            self.spotify.add_tracks_to_playback([track.spotify_uri])
            track.shuffled = True
            self.db.save_scrobble_track(track)
