from _datetime import datetime
from old_src.database import Database


# decorator to make dates readable
def make_date_readable(f):
    def format_unix_date(*args, **kwargs):
        date = f(*args, **kwargs)
        return datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d')
    return format_unix_date


# object for ScrobbleDate
class ScrobbleDate:

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return
        return self.start_date == other.start_date and self.end_date == other.end_date

    def __hash__(self):
        return hash((self.start_date, self.end_date))

    def save(self, db: Database):
        db.save_scrobble_date(self)

    @make_date_readable
    def get_start_date_string(self):
        return self.start_date

    @make_date_readable
    def get_end_date_string(self):
        return self.end_date


def format_track_name(track_name):
    return str(track_name).split(" - ", 1)


# object for ScrobbleTrack
class ScrobbleTrack:

    def __init__(self, lastfm_track=None, track_artist=None, track_name=None, play_count=0, to_be_added=False, in_playlist=False, shuffled=False, spotify_uri=None):
        if lastfm_track is not None:
            formatted_track = format_track_name(lastfm_track.item)
            self.track_artist = formatted_track[0]
            self.track_name = formatted_track[1]
            self.play_count = lastfm_track.weight
        else:
            self.track_artist = track_artist
            self.track_name = track_name
            self.play_count = play_count
        self.to_be_added = bool(to_be_added)
        self.in_playlist = bool(in_playlist)
        self.shuffled = bool(shuffled)
        self.spotify_uri = spotify_uri

    def save(self, db: Database):
        db.save_scrobble_track(self)