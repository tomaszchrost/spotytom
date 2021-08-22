import pylast
import authenticator
from pylast import md5
import requests
from bs4 import BeautifulSoup


LASTFM_API_BASE = 'http://ws.audioscrobbler.com/2.0/'
LASTFM_WEB_REDIRECT_URL = "http://127.0.0.1:5000/lastfm_callback"


# ----------------------------------------------------------------------------------------------------------------------
# web based auth
# ----------------------------------------------------------------------------------------------------------------------


def get_auth_url():
    return f'http://www.last.fm/api/auth/?api_key={authenticator.LASTFM_API_KEY}&cb={LASTFM_WEB_REDIRECT_URL}'


def authorize(token):
    auth_token_url = f"{LASTFM_API_BASE}"
    signature_to_hash = f"api_key{authenticator.LASTFM_API_KEY}methodauth.getSessiontoken{token}{authenticator.LASTFM_API_SECRET}"
    signature = md5(signature_to_hash)

    res = requests.post(auth_token_url, data={
        "method": "auth.getSession",
        "api_key": authenticator.LASTFM_API_KEY,
        "api_sig": signature,
        "token": token
    })

    soup = BeautifulSoup(res.content, features="html.parser")

    return soup.find('key').string, soup.find('name').string


def get_lastfm_with_token(token, username):
    return pylast.LastFMNetwork(session_key=token,
                                api_key=authenticator.LASTFM_API_KEY,
                                api_secret=authenticator.LASTFM_API_SECRET,
                                username=username)

# ----------------------------------------------------------------------------------------------------------------------
# cli based auth
# ----------------------------------------------------------------------------------------------------------------------


def get_lastfm():
    return pylast.LastFMNetwork(api_key=authenticator.LASTFM_API_KEY,
                                api_secret=authenticator.LASTFM_API_SECRET,
                                username=authenticator.LASTFM_USERNAME,
                                password_hash=authenticator.LASTFM_PASSWORD)

