import mysql.connector

DBNAME = "spotytom"


def read_old_scrobble_dates(file_name: str):
    weekly_dates_used = []
    with open(file_name, 'r+') as file:
        for line in file:
            date = line.split(";")
            if len(date) == 2 and date != []:
                weekly_dates_used.append((date[0], date[1].replace('\n', '')))
        file.close()
    return weekly_dates_used


def read_old_tracks(file_name: str):
    track_list = []
    with open(file_name, 'r+') as file:
        for line in file:
            track = line.split(";")
            if len(track) == 3:
                track_list.append((track[0], track[1], track[2].replace('\n', '')))
        file.close()
    return track_list


def mysql_connect(username: str, password: str):
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=password)

    return db


def mysql_connect_to_db(username: str, password: str):
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=password,
        database=DBNAME)

    return db


class Database:

    username = ""
    password = ""

    def __init__(self):
        self.db = self.mysql_initialise_or_connect_db(self.username, self.password)

    def get_cursor(self):
        return self.db.cursor()

    def initialise_db(self):
        cursor = self.get_cursor()
        cursor.execute("CREATE DATABASE " + DBNAME)
        cursor.execute("CREATE TABLE scrobble_dates (start_date VARCHAR(255) NOT NULL, end_date VARCHAR(255) NOT NULL)")
        cursor.execute("CREATE TABLE tracks (track VARCHAR(255) UNIQUE NOT NULL, play_count INT NOT NULL, in_playlist BOOLEAN NOT NULL)")

    def mysql_initialise_or_connect_db(self, username: str, password: str):
        self.db = mysql_connect(username, password)

        found_db = False
        cursor = self.get_db_list()

        for dbname in cursor:
            if dbname == DBNAME:
                found_db = True

        if not found_db:
            self.intialise_db()

        return self.db.mysql_connect_to_db(username, password)

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
        cursor.execute("SELECT * FROM tracks WHERE play_count>=5 AND in_playlist=FALSE")
        return cursor.fetchall()

    def update_track(self, track_object):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM tracks WHERE track=" + track_object[0])
        track_check = cursor.fetchall()

        track_found = False
        for track_to_check in track_check:
            if track_to_check == track_object[0]:
                track_found = True

        if track_found:
            cursor.execute("UPDATE tracks SET play_count=play_count + " + track_object[1] +
                           "WHERE track=" + track_object[0])
        else:
            sql = "INSERT INTO tracks (track, play_count, in_playlist) VALUES (%s, %s, %s)"
            val = (track_object[0], track_object[1], track_object[2])
            cursor.execute(sql, val)

        self.db.commit()

    def update_new_playlist_track(self, track_object):
        cursor = self.get_cursor()
        cursor.execute("UPDATE tracks SET in_playlist=TRUE WHERE track=" + track_object[0])
        self.db.commit()

    def add_scrobble_dates(self, scrobble_dates):
        cursor = self.get_cursor()

        sql = "INSERT INTO scrobble_dates (start_date, end_date) VALUES (%s, %s)"
        val = scrobble_dates
        cursor.execute(sql, val)