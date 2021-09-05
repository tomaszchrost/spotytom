from src.spotify import Spotify
from src.database import Database
from src import scrobble_objects
import logging

play_count_to_be_removed = 5
# used for skipping over issues, if I just need it to work
hide_errors = False


# uses other implemented tasks for carry out processes
class ProcessUpdatePlaylist:

    playlist_name = 'Automated Discover'

    # initialise other classes
    def __init__(self, spotify_token=None, flask_username=None):
        self.spotify = Spotify(spotify_token)
        self.db = Database(flask_username)
        self.ScrobbleData = self.db.get_scrobble_tracks()

    def get_playlist_tracks(self):
        playlist_ids = self.db.get_discover_playlists()
        playlist_tracks = []
        for playlist_id in playlist_ids:
            playlist_tracks.extend(self.spotify.get_songs_from_singular_playlist(playlist_id['id']))
        return playlist_tracks

    def filter_tracks(self, tracks):
        filtered_once_tracks = []
        filtered_twice_tracks = []

        # filter out those already in the playlist
        ignore_playlist = self.spotify.get_playlist_id(self.playlist_name)
        ignore_tracks = self.spotify.get_songs_from_singular_playlist(ignore_playlist)
        for track in tracks:
            add_track = True
            for ignore_track in ignore_tracks:
                if track.spotify_uri == ignore_track.spotify_uri:
                    add_track = False
                    break
            if add_track:
                filtered_once_tracks.append(track)

        # filter out those already listened to
        for track in filtered_once_tracks:
            add_track = True
            related_scrobble_track = None
            for scrobble_track in self.ScrobbleData:
                if track.track_artist == scrobble_track.track_artist and track.track_name == scrobble_track.track_name:
                    related_scrobble_track = scrobble_track
                    if scrobble_track.play_count >= play_count_to_be_removed or scrobble_track.in_discover_playlist:
                        add_track = False
                        break
            if add_track:
                if related_scrobble_track:
                    filtered_twice_tracks.append(related_scrobble_track)
                else:
                    new_scrobble_track = scrobble_objects.ScrobbleTrack(
                            track_name=track.track_name,
                            track_artist=track.track_artist,
                            spotify_uri=track.spotify_uri
                    )
                    filtered_twice_tracks.append(new_scrobble_track)
                print(f'Adding {track.track_artist} - {track.track_name}')
        return filtered_twice_tracks

    def recursive_add_tracks(self, scrobble_track_list):
        if len(scrobble_track_list) == 0:
            return

        # grab first 100 tracks, as limit for spotify api
        scrobble_tracks = scrobble_track_list[:100]
        scrobble_track_list = scrobble_track_list[100:]
        uris_to_send = []

        for scrobble_track in scrobble_tracks:
            if not scrobble_track.spotify_uri:
                scrobble_track.spotify_uri = self.spotify.get_track_uri_from_track_name(scrobble_track.track_artist + " " + scrobble_track.track_name)
                self.db.save_scrobble_track(scrobble_track)
            uris_to_send.append(scrobble_track.spotify_uri)

        self.spotify.add_tracks_max_100(uris_to_send, playlist_id=self.spotify.get_playlist_id(self.playlist_name))

        for scrobble_track in scrobble_tracks:
            scrobble_track.in_discover_playlist = True
            self.db.save_scrobble_track(scrobble_track)

        logging.info("Adding to playlist...")
        if len(uris_to_send) != 0:
            self.recursive_add_tracks(scrobble_track_list)

    def add_tracks(self, tracks):
        self.recursive_add_tracks(tracks)
        logging.info("Finished adding to playlist")

    def update_discover_playlist(self):
        tracks = self.get_playlist_tracks()
        filtered_tracks = self.filter_tracks(tracks)
        self.add_tracks(filtered_tracks)
