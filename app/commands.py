from app import db
from app.models import User
from flask import Flask

from src.database import Database
from src.lastfm import LastFM
from src.spotify.authentication import refresh_token
from src.web_rows import process_update_delete_from_discover_playlist, process_update_discover_playlist, \
    process_update_playlist

import logging


def register_commands(app: Flask):
    import click

    @app.cli.command("add-new-user")
    @click.argument("username")
    @click.argument("password")
    def add_new_user(username: str, password: str):
        u = User(username=username)
        u.set_password(password)

        db.session.add(u)
        db.session.commit()

    @app.cli.command("change-user-password")
    @click.argument("username")
    @click.argument("password")
    def change_user_password(username: str, password: str):
        u = User.query.filter_by(username=username).first()
        u.set_password(password)

        db.session.add(u)
        db.session.commit()

    @app.cli.command("delete-from-all-discovers")
    def delete_from_all_discovers():
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

    @app.cli.command("update-all-best-ofs")
    def update_all_best_ofs():
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
                except Exception as e:
                    logging.error(e)

    @app.cli.command("update-all-discovers")
    def update_all_discovers():
        users = User.query.all()
        for user in users:
            if user.spotify_refresh_token:

                spotify_access_token = refresh_token(user.spotify_refresh_token)
                update_process = process_update_discover_playlist.ProcessUpdatePlaylist(
                    spotify_access_token,
                    user.username)

                try:
                    update_process.update_discover_playlist()
                except Exception as e:
                    logging.error(e)

    @app.cli.command("find-scrobbled-tracks")
    @click.argument("artist")
    def find_scrobbled_tracks(artist: str):

        artist_to_find = artist

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