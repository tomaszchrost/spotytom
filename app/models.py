from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    spotify_refresh_token = db.Column(db.String(256))
    lastfm_username = db.Column(db.String(64))

    updating_playlist = db.Column(db.Boolean, default=False)
    error_updating = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_spotify_refresh_token(self, refresh_token):
        self.spotify_refresh_token = refresh_token

    def set_lastfm_username(self, username):
        self.lastfm_username = username


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
