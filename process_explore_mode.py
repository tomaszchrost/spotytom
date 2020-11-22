from spotify import Spotify


# uses other implemented tasks for carry out processes
class ProcessExploreMode:

    # initialise other classes
    def __init__(self, spotify_token=None):
        self.spotify = Spotify(spotify_token)

    def get_explore_tracks(self, artist_id, track_count, track_array, artist_array):
        if track_count >= 30:
            return track_array

        artist_array.append(artist_id)

        related_artist = self.spotify.get_random_related_artist_unique(artist_id, artist_array)
        next_track = self.spotify.get_random_artist_track(related_artist)

        track_array.append(next_track)
        self.get_explore_tracks(related_artist, track_count + 1, track_array, artist_array)

    def get_first_explore_track(self):
        return self.spotify.get_track_playing()

    def start_explore_mode(self):
        playback_array = []
        artist_playing = self.spotify.get_artist_playing()
        self.get_explore_tracks(artist_playing, 1, playback_array, [artist_playing])
        self.spotify.add_tracks_to_playback(playback_array)
