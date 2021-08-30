from spotipy.oauth2 import SpotifyOAuth
import spotipy
import authenticator
import requests
import base64

SPOTIFY_API_BASE = 'https://accounts.spotify.com'
SHOW_SPOTIFY_DIALOG = True
SPOTIFY_WEB_REDIRECT_URL = "http://127.0.0.1:5000/spotify_callback"
SCOPE = 'playlist-modify-public playlist-modify-private streaming user-read-currently-playing'


def get_auth_url():
    return f'{SPOTIFY_API_BASE}/authorize?client_id={authenticator.SPOTIPY_CLIENT_ID}&response_type=code&redirect_uri={SPOTIFY_WEB_REDIRECT_URL}&scope={SCOPE}&show_dialog={SHOW_SPOTIFY_DIALOG}'


def get_tokens(code):
    auth_token_url = f"{SPOTIFY_API_BASE}/api/token"
    res = requests.post(auth_token_url, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_WEB_REDIRECT_URL,
        "client_id": authenticator.SPOTIPY_CLIENT_ID,
        "client_secret": authenticator.SPOTIPY_CLIENT_SECRET
    })
    res_body = res.json()
    access_token = res_body.get("access_token")
    refresh_token = res_body.get("refresh_token")

    return access_token, refresh_token


def refresh_token(refresh_token):
    auth_token_url = f"{SPOTIFY_API_BASE}/api/token"
    basic_auth = authenticator.SPOTIPY_CLIENT_ID + ":" + authenticator.SPOTIPY_CLIENT_SECRET
    basic_auth_encoded = base64.b64encode(basic_auth.encode())
    res = requests.post(auth_token_url,
        headers={
            "Authorization": "Basic " + basic_auth_encoded.decode()
        },
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )
    res_body = res.json()
    access_token = res_body.get("access_token")
    return access_token


# get user object to connect
def get_user_object():
    auth_manager = SpotifyOAuth(
        scope=SCOPE,
        username=authenticator.spotify_username,
        client_id=authenticator.SPOTIPY_CLIENT_ID,
        client_secret=authenticator.SPOTIPY_CLIENT_SECRET,
        redirect_uri=authenticator.SPOTIPY_REDIRECT_URI
    )

    if auth_manager:
        return spotipy.Spotify(auth_manager=auth_manager)


def get_user_with_token(token):
    return spotipy.Spotify(auth=token)
