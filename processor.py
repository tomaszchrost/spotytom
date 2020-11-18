from lastfm import LastFM
from spotify import Spotify
from database import Database
import scrobble_objects

play_count_to_be_added = 5

# TODO standardise print outputs to stdout
# error when db returns multiple tracks of the name, shouldn't ever happen
class UniqueIndexException(Exception):
    """Raised when more than one of a unique index found"""
    pass


# case insensitive string equal check
def string_equal(str1, str2):
    return str1.lower() == str2.lower()


# uses other implemented tasks for carry out processes
class Processor:

    # initialise other classes
    def __init__(self, spotify_token=None, lastfm_token=None, flask_username=None, lastfm_username=None):
        self.lastfm = LastFM(lastfm_token, lastfm_username)
        self.spotify = Spotify(spotify_token)
        self.db = Database(flask_username)
        self.ScrobbleData = self.db.get_scrobble_tracks()

    # get dates not yet added to db
    def get_new_dates(self):
        lastfm_dates = self.lastfm.get_scrobble_dates()
        db_dates = self.db.get_scrobble_dates()

        return list(set(lastfm_dates) - set(db_dates))

    # searches last fm for new tracks and updates scrobble data
    def update_with_new_scrobble_tracks(self):
        new_dates = self.get_new_dates()

        for date in new_dates:
            new_tracks = self.lastfm.get_scrobbles(date)
            for track in new_tracks:
                matching_tracks = [x
                                   for x in self.ScrobbleData
                                   if string_equal(x.track_name, track.track_name)
                                   and string_equal(x.track_artist, track.track_artist)]
                try:
                    # find match and increase play count
                    if len(matching_tracks) == 1:
                        matching_track = matching_tracks[0]
                        matching_track.play_count += track.play_count
                        matching_track.save(self.db)
                        print("Updated play count of " + track.track_artist + " - " + track.track_name)
                    # add new track
                    elif len(matching_tracks) == 0:
                        self.ScrobbleData.append(track)
                        track.save(self.db)
                        print("Added new track " + track.track_artist + " - " + track.track_name)
                    else:
                        raise UniqueIndexException

                except UniqueIndexException:
                    print("Two matching tracks found, unique index error!")
            date.save(self.db)
            print("Finished with dates " + date.get_start_date_string() + " to " + date.get_end_date_string())

    # searches for new songs added to playlists and updates scrobble data
    def update_with_new_playlist_tracks(self):
        spotify_tracks = self.spotify.get_songs_from_playlists()
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
                        print(matching_track.track_artist + " - " + matching_track.track_name + " set to be added to playlist")
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

    # evaluates tracks that should be added to playlist
    def update_tracks_to_be_added(self):
        for track in self.ScrobbleData:
            if not track.to_be_added and not track.in_playlist and track.play_count >= play_count_to_be_added:
                track.to_be_added = True
                track.save(self.db)
                print(track.track_artist + " - " + track.track_name + " set to be added to playlist")

    # update uris of tracks to be added
    def update_uris(self):
        for track in self.ScrobbleData:
            if not track.in_playlist and track.to_be_added and track.spotify_uri is None:
                track.spotify_uri = self.spotify.get_track_uri_from_track_name(track.track_artist + " " + track.track_name)
                if track.spotify_uri is None:
                    track.spotify_uri = "FAILED"
                    print("URI Error for " + track.track_artist + " - " + track.track_name)
                else:
                    print("URI updated for " + track.track_artist + " - " + track.track_name)
                track.save(self.db)

    def recursive_add_tracks(self, scrobble_track_list):
        if len(scrobble_track_list) == 0:
            return

        # grab first 100 tracks, as limit for spotify api
        scrobble_tracks = scrobble_track_list[:100]
        scrobble_track_list = scrobble_track_list[100:]
        uris_to_send = []

        for scrobble_track in scrobble_tracks:
            uris_to_send.append(scrobble_track.spotify_uri)
        self.spotify.add_tracks_max_100(uris_to_send)
        for scrobble_track in scrobble_tracks:
            scrobble_track.in_playlist = True
            scrobble_track.save(self.db)

        print("Adding to playlist...")
        if len(uris_to_send) != 0:
            self.recursive_add_tracks(scrobble_track_list)

    def add_tracks_to_be_added_to_playlist(self):
        tracks_to_add = []
        for track in self.ScrobbleData:
            if not track.in_playlist and track.to_be_added and track.spotify_uri is not None and track.spotify_uri != "FAILED":
                tracks_to_add.append(track)

        self.recursive_add_tracks(tracks_to_add)
        print("Finished adding to playlist")

    def update_best_of_playlist(self):
        self.update_with_new_scrobble_tracks()
        self.update_with_new_playlist_tracks()
        self.update_tracks_to_be_added()
        self.update_uris()
        self.add_tracks_to_be_added_to_playlist()

    # TODO REFACTOR
    """
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

    def update_best_of_playlist(self):
        self.update_new_tracks()
        self.set_songs_to_bed_added()
        self.update_new_playlist_tracks()
        self.add_uris()
        self.add_tracks_to_playlist()

    def start_explore_mode(self):
        playback_array = [self.get_first_explore_track()]
        artist_playing = self.spotify.get_artist_playing()
        self.get_explore_tracks(artist_playing, 1, playback_array, [artist_playing])
        self.spotify.add_tracks_to_playback(playback_array)"""