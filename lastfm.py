import pylast
import authenticator


def get_user_object():
    return pylast.LastFMNetwork(api_key=authenticator.lastfm_api_key,
                                api_secret=authenticator.lastfm_api_secret,
                                username=authenticator.lastfm_username,
                                password_hash=authenticator.lastfm_password).get_authenticated_user()


class LastFM:

    def __init__(self):
        self.user = get_user_object()

    def get_scrobble_dates(self):
        return self.user.get_weekly_chart_dates()

    # returns track.item and track.weight
    def get_scrobbles(self, start_date, end_date):
        return self.user.get_weekly_track_charts(from_date=start_date, to_date=end_date)
