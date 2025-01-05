import pylast
import authenticator
from pylast import md5
import requests
from bs4 import BeautifulSoup


LASTFM_API_BASE = 'http://ws.audioscrobbler.com/2.0/'
LASTFM_WEB_REDIRECT_URL = "http://127.0.0.1:5000/lastfm_callback"


def get_auth_url():
    return f'http://www.last.fm/api/auth/?api_key={authenticator.lastfm_api_key}&cb={LASTFM_WEB_REDIRECT_URL}'


def authorize(token):
    auth_token_url = f"{LASTFM_API_BASE}"
    signature_to_hash = f"api_key{authenticator.lastfm_api_key}methodauth.getSessiontoken{token}{authenticator.lastfm_api_secret}"
    signature = md5(signature_to_hash)

    res = requests.post(auth_token_url, data={
        "method": "auth.getSession",
        "api_key": authenticator.lastfm_api_key,
        "api_sig": signature,
        "token": token
    })

    soup = BeautifulSoup(res.content, features="lxml")

    return soup.find('key').string, soup.find('name').string


# get user object with authentication data
def get_user():
    return pylast.LastFMNetwork(api_key=authenticator.lastfm_api_key,
                                api_secret=authenticator.lastfm_api_secret,
                                username=authenticator.lastfm_username,
                                password_hash=authenticator.lastfm_password).get_authenticated_user()


def get_pylast():
    return pylast.LastFMNetwork(api_key=authenticator.lastfm_api_key,
                                api_secret=authenticator.lastfm_api_secret,
                                username=authenticator.lastfm_username,
                                password_hash=authenticator.lastfm_password)


def get_user_with_token(token, username):
    return pylast.LastFMNetwork(session_key=token,
                                api_key=authenticator.lastfm_api_key,
                                api_secret=authenticator.lastfm_api_secret,
                                username=username).get_authenticated_user()