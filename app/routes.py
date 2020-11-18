from app import app
from flask import render_template, flash, redirect, url_for, request, session
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
import spotipy
import authenticator
from spotify import get_scope
import requests
from processor import Processor
from pylast import md5
from bs4 import BeautifulSoup
from app import db
import threading
import copy


@app.route('/')
@app.route('/index')
@login_required
def index():
    spotify_verified = True if "spotify_toke" in session else False
    lastfm_verified = True if "lastfm_key" in session else False
    return render_template('index.html', title='Home', spotify_verified=spotify_verified, lastfm_verified=lastfm_verified)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        # find user object
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        # get next page
        session.clear()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# SPOTIFY ROUTES
SPOTIFY_API_BASE = 'https://accounts.spotify.com'
SHOW_SPOTIFY_DIALOG = True
SPOTIFY_WEB_REDIRECT_URL = "http://127.0.0.1:5000/spotify_callback"


@app.route('/verify_spotify')
def verify_spotify():
    auth_url = f'{SPOTIFY_API_BASE}/authorize?client_id={authenticator.SPOTIPY_CLIENT_ID}&response_type=code&redirect_uri={SPOTIFY_WEB_REDIRECT_URL}&scope={get_scope()}&show_dialog={SHOW_SPOTIFY_DIALOG}'
    return redirect(auth_url)


@app.route('/spotify_callback')
def spotify_callback():
    session.pop('spotify_toke', None)
    code = request.args.get('code')

    auth_token_url = f"{SPOTIFY_API_BASE}/api/token"
    res = requests.post(auth_token_url, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_WEB_REDIRECT_URL,
        "client_id": authenticator.SPOTIPY_CLIENT_ID,
        "client_secret": authenticator.SPOTIPY_CLIENT_SECRET
    })

    res_body = res.json()
    session["spotify_toke"] = res_body.get("access_token")

    return redirect(url_for("index"))


# LASTFM ROUTES
LASTFM_API_BASE = 'http://ws.audioscrobbler.com/2.0/'
LASTFM_WEB_REDIRECT_URL = "http://127.0.0.1:5000/lastfm_callback"


@app.route('/verify_lastfm')
def verify_lastfm():
    auth_url = f'http://www.last.fm/api/auth/?api_key={authenticator.lastfm_api_key}&cb={LASTFM_WEB_REDIRECT_URL}'
    return redirect(auth_url)


@app.route('/lastfm_callback')
def lastfm_callback():
    token = request.args.get('token')
    auth_token_url = f"{LASTFM_API_BASE}"
    signature_to_hash = f"api_key{authenticator.lastfm_api_key}methodauth.getSessiontoken{token}{authenticator.lastfm_api_secret}"
    signature = md5(signature_to_hash)

    res = requests.post(auth_token_url, data={
        "method": "auth.getSession",
        "api_key": authenticator.lastfm_api_key,
        "api_sig": signature,
        "token": token
    })

    soup = BeautifulSoup(res.content, features="html.parser")

    current_user.lastfm_key = soup.find('key').string
    current_user.lastfm_name = soup.find('name').string
    db.session.commit()
    return redirect(url_for("index"))


def new_thread_update_playlist(spoty_toke, user_id):
    user = User.query.get(user_id)
    try:
        processor = Processor(
            spoty_toke,
            user.lastfm_key,
            user.username,
            user.lastfm_name
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


@app.route('/update_playlist')
def update_playlist():
    current_user.error_updating = False
    current_user.updating_playlist = True
    db.session.commit()
    update_thread = threading.Thread(target=new_thread_update_playlist, args=(
        session['spotify_toke'],
        current_user.id,
    ))
    update_thread.start()
    return redirect("index")
