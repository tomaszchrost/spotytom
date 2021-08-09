from app import app
from flask import render_template, flash, redirect, url_for, request, session
from app.forms import LoginForm, AddPlaylistForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
import authenticator
import src.spotify.authentication as spotify_authentication
import src.lastfm.authentication as lastfm_authentication
import requests
from src.web_rows.process_update_playlist import ProcessUpdatePlaylist
from src.web_rows.process_explore_mode import ProcessExploreMode
from src.web_rows.process_smart_shuffle import ProcessSmartShuffle
from src.web_rows.process_add_playlist import ProcessAddPlaylist
from pylast import md5
from bs4 import BeautifulSoup
from app import db
import threading
from app.utils import refresh_tokens, run_in_new_thread, run_update_playlist


@app.route('/')
@app.route('/index')
@login_required
def index():
    spotify_verified = True if "spotify_token" in session and "spotify_refresh_token" in session else False
    lastfm_verified = True if "lastfm_key" in session else False
    # TODO how would I do multiple forms?
    form = AddPlaylistForm()
    return render_template('index.html', spotify_verified=spotify_verified, lastfm_verified=lastfm_verified, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/verify_spotify')
def verify_spotify():
    return redirect(spotify_authentication.get_auth_url())


@app.route('/verify_lastfm')
def verify_lastfm():
    return redirect(lastfm_authentication.get_auth_url())


@app.route('/spotify_callback')
def spotify_callback():
    session.pop('spotify_token', None)
    session.pop('spotify_refresh_token', None)

    code = request.args.get('code')
    session["spotify_token"], session["spotify_refresh_token"] = spotify_authentication.get_tokens(code)

    return redirect(url_for("index"))


@app.route('/lastfm_callback')
def lastfm_callback():
    token = request.args.get('token')
    session["lastfm_key"], session["lastfm_name"] = lastfm_authentication.authorize(token)

    return redirect(url_for("index"))


@refresh_tokens
@app.route('/update_playlist')
def update_playlist():
    run_update_playlist()
    return redirect("index")


@refresh_tokens
@app.route('/explore_mode')
def explore_mode():
    processor = ProcessExploreMode(session["spotify_token"])
    processor.start_explore_mode()
    return redirect("index")


@refresh_tokens
@app.route('/smart_shuffle')
def smart_shuffle():
    processor = ProcessSmartShuffle(session["spotify_token"], current_user.username)
    processor.start_smart_shuffle()
    return redirect("index")


@refresh_tokens
@app.route('/add_playlist', methods=['POST'])
def add_playlist():
    form = AddPlaylistForm()
    processor = ProcessAddPlaylist(form.playlist_id.data, session["spotify_token"], current_user.username)
    processor.add_playlist_tracks()
    return redirect("index")
