from app.models import User
from src.spotify.authentication import refresh_token
from src.web_rows import process_update_playlist
import logging


def main():

    # for all users, loop through and try to update playlists if viable for update
    # get all users
    # check user has lastfm_username and spotify_refresh_token set
    # call web_row process for each user
    users = User.query.all()
    for user in users:
        if user.lastfm_username and user.spotify_refresh_token:

            spotify_access_token = refresh_token(user.spotify_refresh_token)
            update_process = process_update_playlist.ProcessUpdatePlaylist(
                    spotify_access_token,
                    user.username,
                    user.lastfm_username)

            try:
                update_process.update_best_of_playlist()
            except Exception:
                logging.error(Exception)


if __name__ == "__main__":
    main()
