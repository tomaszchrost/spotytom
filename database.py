import mysql.connector


def mysql_connect(username: str, password: str):
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=password,
        database="spotifybestbits"
    )

    return db


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

class Database:

    def __init__(self, username, password):
        self.db = mysql_connect(username, password)

    def get_cursor(self):
        return self.db.cursor()

    def get_scrobble_dates(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM scrobble_dates")
        return cursor.fetchall()

    def get_tracks(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM tracks")
        return cursor.fetchall()

def findNewWeeks(user):
    weekly_dates_used = readUsedWeeklyDates()

    weekly_dates = getWeeklyDates(user)

    weekly_dates_new = []

    for week in weekly_dates:
        weekly_dates_new.append(week)

    new_weeks = []
    weeks_found = 0
    for week in weekly_dates_new:
        if (week not in weekly_dates_used):
            new_weeks.append(week)
            weeks_found = weeks_found + 1
    print("New weeks found: " + str(weeks_found))
    return new_weeks

def updateTrackFile():
    # set user, new weeks, and current track list
    lastfm = lastFMUser()
    new_weeks = findNewWeeks(lastfm)
    track_list = getTrackList()

    # reverse to make testing quicker, as only using recently
    new_weeks.reverse()

    for week in new_weeks:

        # get tracks for week and output how many unique tracks
        week_tracks = lastfm.get_weekly_track_charts(from_date=week[0], to_date=week[1])
        print("Adding " + str(len(week_tracks)) + " unique tracks")

        # then grab track individually
        for new_track in week_tracks:

            # boolean if already exists
            track_exists = False

            # for each
            for old_track_index in range(len(track_list)):

                if (str(new_track.item) == str(track_list[old_track_index][0])):
                    track_list[old_track_index] = (
                    track_list[old_track_index][0], str(int(track_list[old_track_index][1]) + int(new_track.weight)),
                    track_list[old_track_index][2])
                    track_exists = True
                    break

            if not track_exists:
                track_list.append((new_track.item, new_track.weight, "False"))

        with open('dates.txt', 'a+') as file:
            file.write('\n' + ';'.join(week))
        file.close()

        with open('tracks.txt', 'w+') as file:
            for track in track_list:
                try:
                    file.write('\n' + str(track[0]) + ";" + str(track[1]) + ";" + str(track[2]))
                except UnicodeEncodeError:
                    print("Issue with encodng")
            file.close()
        print("Length of file: " + str(len(track_list)))
        time.sleep(1)

        def getSongsForPlaylist():
            playlist_list = []
            track_list = getTrackList()
            for track in track_list:
                if len(track) == 3 and track[2] == "False" and int(track[1]) >= 5:
                    playlist_list.append(track[0])
            return playlist_list

        def setPlaylistSongsToTrue():
            playlist_list = []
            track_list = getTrackList()
            for track_index in range(len(track_list)):
                if track_list[track_index][2] == "False" and int(track_list[track_index][1]) >= 5:
                    track_list[track_index] = (track_list[track_index][0], track_list[track_index][1], "True")
            with open('tracks.txt', 'w+') as file:
                for track in track_list:
                    file.write('\n' + str(track[0]) + ";" + str(track[1]) + ";" + str(track[2]))
                file.close()
            print("File Saved")