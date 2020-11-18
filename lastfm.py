import pylast
import authenticator
import scrobble_objects


# get user object with authentication data
def get_user_object():
    return pylast.LastFMNetwork(api_key=authenticator.lastfm_api_key,
                                api_secret=authenticator.lastfm_api_secret,
                                username=authenticator.lastfm_username,
                                password_hash=authenticator.lastfm_password).get_authenticated_user()


def get_user_with_token(token, username):
    return pylast.LastFMNetwork(session_key=token,
                                api_key=authenticator.lastfm_api_key,
                                api_secret=authenticator.lastfm_api_secret,
                                username=username).get_authenticated_user()


# start date return from last fm date
def get_scrobble_start_date(date):
    return date[0]


# end date return from last fm date
def get_scrobble_end_date(date):
    return date[1]


def last_fm_scrobble_date_object(f):
    def last_fm_to_scrobble_dates(*args, **kwargs):
        last_fm_dates = f(*args, **kwargs)
        scrobble_date_objects = []
        for date in last_fm_dates:
            scrobble_date_objects.append(
                scrobble_objects.ScrobbleDate(
                    get_scrobble_start_date(date),
                    get_scrobble_end_date(date)
                )
            )
        return scrobble_date_objects
    return last_fm_to_scrobble_dates


def last_fm_scrobble_track_object(f):
    def last_fm_to_scrobble_tracks(*args, **kwargs):
        last_fm_tracks = f(*args, **kwargs)
        scrobble_track_objects = []
        for track in last_fm_tracks:
            scrobble_track_objects.append(scrobble_objects.ScrobbleTrack(track))
        return scrobble_track_objects
    return last_fm_to_scrobble_tracks


# object for lastfm
class LastFM:

    def __init__(self, token=None, username=None):
        if token:
            self.user = get_user_with_token(token, username)
        else:
            self.user = get_user_object()

    @last_fm_scrobble_date_object
    def get_scrobble_dates(self):
        lastfm_dates = self.user.get_weekly_chart_dates()
        return lastfm_dates

    @last_fm_scrobble_track_object
    def get_scrobbles(self, date: scrobble_objects.ScrobbleDate):
        lastfm_track = self.user.get_weekly_track_charts(from_date=date.start_date, to_date=date.end_date)
        return lastfm_track
