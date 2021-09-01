from app.models import User
from src.spotify.authentication import refresh_token
from src.web_rows import process_update_playlist
import logging
from src.lastfm import LastFM
from src.database import Database


def main():

    artist_to_find = 'Orla Gartland'

    users = User.query.all()
    for user in users:
        if user.lastfm_username:
            print('User: ' + user.username)
            database = Database(user.username)
            scrobble_dates = database.get_scrobble_dates()
            lastfm = LastFM(user.lastfm_username)
            for scrobble_date in scrobble_dates:
                scrobbles = lastfm.get_scrobbles(scrobble_date)
                for scrobble in scrobbles:
                    if scrobble.track_artist == artist_to_find:
                        print(scrobble.track_artist + ' - ' + scrobble.track_name + ' ' + str(scrobble.play_count))


if __name__ == "__main__":
    main()
