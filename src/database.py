import MySQLdb
import authenticator
import src.scrobble_objects as scrobble_objects
import logging

DBNAME = "spotytom"


class TableSearchException(Exception):
    """Raised when tables could not be found"""
    pass


# connect to localhost
def mysql_connect():
    db = MySQLdb.connect(
        host="localhost",
        user=authenticator.db_username,
        passwd=authenticator.db_password,
        charset="utf8")

    return db


# connect to localhost with specified db
def mysql_connect_to_db():
    db = MySQLdb.connect(
        host="localhost",
        user=authenticator.db_username,
        passwd=authenticator.db_password,
        database=DBNAME,
        charset="utf8")

    return db


# decorator for db dates
def db_scrobble_date_object(f):
    def db_to_scrobble_dates(*args, **kwargs):
        db_dates = f(*args, **kwargs)
        scrobble_date_objects = []
        for date in db_dates:
            scrobble_date_objects.append(scrobble_objects.ScrobbleDate(date["start_date"], date["end_date"]))

        return scrobble_date_objects

    return db_to_scrobble_dates


# decorator for db tracks
def db_scrobble_track_object(f):
    def db_to_scrobble_tracks(*args, **kwargs):
        db_tracks = f(*args, **kwargs)
        scrobble_track_objects = []
        for track in db_tracks:
            scrobble_track_objects.append(
                scrobble_objects.ScrobbleTrack(
                    track_artist=track["track_artist"],
                    track_name=track["track_name"],
                    play_count=track["play_count"],
                    to_be_added=track["to_be_added"],
                    in_playlist=track["in_playlist"],
                    shuffled=track["shuffled"],
                    spotify_uri=track["spotify_uri"]
                )
            )
        return scrobble_track_objects

    return db_to_scrobble_tracks


class Database:

    def __init__(self, username=None):
        self.username = username
        self.mysql_initialise_or_connect_db()

    def get_cursor(self):
        return self.db.cursor(MySQLdb.cursors.DictCursor)

    def initialise_db(self):
        cursor = self.get_cursor()
        cursor.execute("CREATE DATABASE " + DBNAME + " CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
        self.db = mysql_connect_to_db()

    def initialise_date_table(self):
        logging.info("executing_date_table")
        cursor = self.get_cursor()
        cursor.execute(f"CREATE TABLE {self.username}_scrobble_dates (start_date VARCHAR(255) NOT NULL, end_date VARCHAR(255) NOT NULL)")

    def initialise_discover_playlist_table(self):
        logging.info("executing_playlist_table")
        cursor = self.get_cursor()
        cursor.execute(f"CREATE TABLE {self.username}_discover_playlists (id VARCHAR(255) NOT NULL)")

    def initialise_track_table(self):
        logging.info("executing_track_table")
        cursor = self.get_cursor()
        cursor.execute(f"""CREATE TABLE {self.username}_scrobble_tracks (
                       track_artist VARCHAR(255) NOT NULL,
                       track_name VARCHAR(255) NOT NULL,
                       play_count INT NOT NULL,
                       to_be_added BOOLEAN NOT NULL DEFAULT FALSE,
                       in_playlist BOOLEAN NOT NULL DEFAULT FALSE,
                       shuffled BOOLEAN NOT NULL DEFAULT FALSE,
                       spotify_uri VARCHAR(255) DEFAULT NULL,
                       PRIMARY KEY(track_artist, track_name)
                       )""")

    def check_table_exists(self, tablename):
        cursor = self.get_cursor()
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{tablename}'
            """)
        if cursor.fetchone()['COUNT(*)'] == 1:
            cursor.close()
            return True

        return False

    def mysql_initialise_or_connect_db(self):
        self.db = mysql_connect()

        found_db = False
        cursor = self.get_db_list()

        for dbname in cursor:
            if dbname["Database"] == DBNAME:
                found_db = True

        if not found_db:
            self.initialise_db()

        self.db = mysql_connect_to_db()

        found_date_table = self.check_table_exists(f'{self.username}_scrobble_dates')
        found_track_table = self.check_table_exists(f'{self.username}_scrobble_tracks')
        found_playlist_table = self.check_table_exists(f'{self.username}_discover_playlists')
        if not found_date_table:
            self.initialise_date_table()
        if not found_track_table:
            self.initialise_track_table()
        if not found_playlist_table:
            self.initialise_discover_playlist_table()
        found_date_table = self.check_table_exists(f'{self.username}_scrobble_dates')
        found_track_table = self.check_table_exists(f'{self.username}_scrobble_tracks')
        found_playlist_table = self.check_table_exists(f'{self.username}_discover_playlists')
        if not (found_track_table or found_date_table or found_playlist_table):
            raise TableSearchException

    def get_db_list(self):
        cursor = self.get_cursor()
        cursor.execute("SHOW DATABASES")
        return cursor

    @db_scrobble_date_object
    def get_scrobble_dates(self):
        cursor = self.get_cursor()
        cursor.execute(f"SELECT * FROM {self.username}_scrobble_dates")
        return cursor.fetchall()

    @db_scrobble_track_object
    def get_scrobble_tracks(self):
        cursor = self.get_cursor()
        cursor.execute(f"SELECT * FROM {self.username}_scrobble_tracks")
        return cursor.fetchall()

    def get_discover_playlists(self):
        cursor = self.get_cursor()
        cursor.execute(f"SELECT * FROM {self.username}_discover_playlists")
        return cursor.fetchall()

    def save_scrobble_date(self, scrobble_date):
        cursor = self.get_cursor()

        sql = f"INSERT INTO {self.username}_scrobble_dates (start_date, end_date) VALUES (%s, %s)"
        val = (scrobble_date.start_date, scrobble_date.end_date)
        cursor.execute(sql, val)
        self.db.commit()

    def save_scrobble_track(self, scrobble_track):
        cursor = self.get_cursor()

        sql = f"""INSERT INTO {self.username}_scrobble_tracks (track_artist, track_name, play_count, to_be_added, in_playlist, shuffled, spotify_uri) VALUES (%s, %s, %s, %s, %s, %s, %s)
                 ON DUPLICATE KEY UPDATE play_count=VALUES(play_count),
                                         to_be_added=VALUES(to_be_added),
                                         in_playlist=VALUES(in_playlist),
                                         shuffled=VALUES(shuffled),
                                         spotify_uri=VALUES(spotify_uri)"""
        val = (scrobble_track.track_artist,
               scrobble_track.track_name,
               scrobble_track.play_count,
               scrobble_track.to_be_added,
               scrobble_track.in_playlist,
               scrobble_track.shuffled,
               scrobble_track.spotify_uri)
        cursor.execute(sql, val)
        self.db.commit()

    def save_discover_playlists(self, playlist_id):
        cursor = self.get_cursor()

        sql = f"""INSERT INTO {self.username}_discover_playlists (id) VALUES ({playlist_id})"""
        cursor.execute(sql)
        self.db.commit()
