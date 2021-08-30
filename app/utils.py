from flask import session
from flask_login import current_user
from src.spotify.authentication import refresh_token
import threading
from app import db
from app.models import User
from src.web_rows.process_update_playlist import ProcessUpdatePlaylist
from flask_login import current_user


def refresh_tokens(f):
    def refresh_tokens_decorator(*args, **kwargs):
        session['spotify_token'] = refresh_token(current_user.spotify_refresh_token)
        return f(*args, **kwargs)
    return refresh_tokens_decorator


def run_in_new_thread(f):
    def run_in_new_thread_decorator(*args, **kwargs):
        new_thread = threading.Thread(target=f, args=args, kwargs=kwargs)
        new_thread.start()
    return run_in_new_thread_decorator


def run_update_playlist():

    @refresh_tokens
    @run_in_new_thread
    def update_playlist(spotify_token, lastfm_name, user_id):
        user = User.query.get(user_id)
        try:
            processor = ProcessUpdatePlaylist(
                spotify_token,
                user.username,
                lastfm_name
            )
            processor.update_best_of_playlist()
        except Exception as e:
            user.updating_playlist = False
            user.error_updating = True
            db.session.commit()
            raise e
        else:
            user.updating_playlist = False
            db.session.commit()

    current_user.error_updating = False
    current_user.updating_playlist = True
    db.session.commit()
    update_playlist(
        session['spotify_token'],
        session['lastfm_name'],
        current_user.id,
    )
