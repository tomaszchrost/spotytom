import pylast


def get_user_object(username, password_hash, api_key, api_secret):
    return pylast.LastFMNetwork(api_key=api_key,
                                api_secret=api_secret,
                                username=username,
                                password_hash=password_hash).get_authenticated_user()


class LastFM:

    def __init__(self, username, password_hash, api_key, api_secret):
        self.user = get_user_object(username, password_hash, api_key, api_secret)

    def get_scrobble_dates(self):
        return self.user.get_weekly_chart_dates()

    def get_scrobbles(self, start_date, end_date):
        return self.user.get_weekly_track_charts(from_date=start_date, to_date=end_date)


