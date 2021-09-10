from app.models import User
from src.spotify.authentication import refresh_token
from src.web_rows import process_update_delete_from_discover_playlist
import logging


def main():
    users = User.query.all()
    for user in users:
        if user.spotify_refresh_token:

            spotify_access_token = refresh_token(user.spotify_refresh_token)
            update_process = process_update_delete_from_discover_playlist.ProcessDeleteFromPlaylist(
                    spotify_access_token,
                    user.username)

            try:
                update_process.delete_from_playlist()
            except Exception as e:
                print(user.username, e)


if __name__ == "__main__":
    main()
