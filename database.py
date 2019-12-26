import mysql.connector
import communicator
import authenticator

DBNAME = "spotytom"


def mysql_connect():
    db = mysql.connector.connect(
        host="localhost",
        user=authenticator.db_username,
        passwd=authenticator.db_password)

    return db


def mysql_connect_to_db():
    db = mysql.connector.connect(
        host="localhost",
        user=authenticator.db_username,
        passwd=authenticator.db_password,
        database=DBNAME)

    return db


class Database:

    def __init__(self):
        self.db = self.mysql_initialise_or_connect_db()

    def get_cursor(self):
        return self.db.cursor()

    def initialise_db(self):
        cursor = self.get_cursor()
        cursor.execute("CREATE DATABASE " + DBNAME + " CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        self.db = mysql_connect_to_db()
        cursor = self.get_cursor()
        cursor.execute("CREATE TABLE scrobble_dates (start_date VARCHAR(255) NOT NULL, end_date VARCHAR(255) NOT NULL)")
        cursor.execute("CREATE TABLE tracks (" +
                       "track VARCHAR(255) UNIQUE NOT NULL," +
                       "play_count INT NOT NULL," +
                       "to_be_added BOOLEAN NOT NULL DEFAULT FALSE," +
                       "in_playlist BOOLEAN NOT NULL DEFAULT FALSE," +
                       "spotify_uri VARCHAR(255) DEFAULT NULL" +
                       ")")

    def mysql_initialise_or_connect_db(self):
        self.db = mysql_connect()

        found_db = False
        cursor = self.get_db_list()

        for dbname in cursor:
            if dbname[0] == DBNAME:
                found_db = True

        if not found_db:
            self.initialise_db()

        return mysql_connect_to_db()

    def get_db_list(self):
        cursor = self.get_cursor()
        cursor.execute("SHOW DATABASES")
        return cursor

    def get_scrobble_dates(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM scrobble_dates")
        return cursor.fetchall()

    def get_tracks(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM tracks")
        return cursor.fetchall()

    def get_tracks_for_playlist(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM tracks WHERE to_be_added=TRUE AND in_playlist=FALSE AND spotify_uri IS NOT NULL")
        return cursor.fetchall()

    def get_tracks_for_uris(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM tracks WHERE to_be_added=TRUE AND in_playlist=FALSE AND spotify_uri IS NULL")
        return cursor.fetchall()

    def update_track(self, track_object):
        cursor = self.get_cursor()

        cursor.execute("INSERT INTO tracks SET track = '" + track_object[0]
                       +"', play_count = " + str(track_object[1])
                       + " ON DUPLICATE KEY UPDATE play_count=play_count+" + str(track_object[1]))
        self.db.commit()
        # communicator.output_track_to_db(track_object[0])

    def update_track_from_playlist(self, track_name):
        cursor = self.get_cursor()

        cursor.execute("INSERT INTO tracks SET track = '" + str(track_name)
                       +"', play_count = 0"
                       + " ON DUPLICATE KEY UPDATE to_be_added=TRUE")
        self.db.commit()
        # communicator.output_track_to_db(track_name)

    def update_to_be_added_playlist(self):
        cursor = self.get_cursor()
        cursor.execute("UPDATE tracks SET to_be_added=TRUE WHERE play_count >= 5")
        self.db.commit()

    def update_new_playlist_track(self, track_object):
        cursor = self.get_cursor()
        cursor.execute("UPDATE tracks SET in_playlist=TRUE WHERE track='" + str(track_object) + "'")
        self.db.commit()

    def add_track_uri(self, track_name, uri):
        cursor = self.get_cursor()
        cursor.execute("UPDATE tracks SET spotify_uri='" + uri + "' WHERE track='" + str(track_name) + "'")
        self.db.commit()

    def add_scrobble_date(self, scrobble_date):
        cursor = self.get_cursor()

        sql = "INSERT INTO scrobble_dates (start_date, end_date) VALUES (%s, %s)"
        val = (scrobble_date[0], scrobble_date[1])
        cursor.execute(sql, val)
        self.db.commit()
