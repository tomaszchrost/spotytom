import pylast
import json
from datetime import datetime
import collections
import time
import sys
import spotipy
import spotipy.util as util

"""
Application name
API key
Shared secret
Registered to
"""

def convertTupleToInt(tup):
    newtup = ''.join(tup)
    newtup = int(newtup)
    return newtup

def lastFMUser():
    username = "temp user"
    password_hash = pylast.md5("temp pass")
    API_KEY = "temp key"
    API_SECRET = "temp secret"
    lastfm = pylast.LastFMNetwork(api_key = API_KEY, api_secret = API_SECRET, username = username, password_hash = password_hash)
    me = lastfm.get_authenticated_user()
    return me

def getWeeklyDates(user):
    weekly_dates = user.get_weekly_chart_dates()
    return weekly_dates

def readUsedWeeklyDates():
    weekly_dates_used = []
    with open('dates.txt', 'r+') as file:
        for line in file:
            date = line.split(";")
            if(len(date) == 2 and date != []):
                weekly_dates_used.append((date[0],date[1].replace('\n', '')))
    return weekly_dates_used

def findNewWeeks(user):
    weekly_dates_used = readUsedWeeklyDates()
                  
    weekly_dates = getWeeklyDates(user)
    
    weekly_dates_new = []
    
    for week in weekly_dates:
        weekly_dates_new.append(week)

    new_weeks = []
    weeks_found = 0
    for week in weekly_dates_new:
        if(week not in weekly_dates_used):
            new_weeks.append(week)
            weeks_found = weeks_found + 1
    print("New weeks found: " + str(weeks_found))
    return new_weeks

def getTrackList():
    track_list = []
    with open('tracks.txt', 'r+') as file:
        for line in file:
            track = line.split(";")
            if(len(track) == 3):
                track_list.append((track[0],track[1],track[2].replace('\n', '')))
    file.close()
    return track_list

def updateTrackFile():
    #set user, new weeks, and current track list
    lastfm = lastFMUser()
    new_weeks = findNewWeeks(lastfm)
    track_list = getTrackList()

    #reverse to make testing quicker, as only using recently            
    new_weeks.reverse()
    
    for week in new_weeks:

        #get tracks for week and output how many unique tracks
        week_tracks = lastfm.get_weekly_track_charts(from_date=week[0], to_date=week[1])
        print("Adding " + str(len(week_tracks)) + " unique tracks")

        #then grab track individually
        for new_track in week_tracks:

            #boolean if already exists
            track_exists = False

            #for each
            for old_track_index in range(len(track_list)):
                
                if(str(new_track.item) == str(track_list[old_track_index][0])):
                    track_list[old_track_index] = (track_list[old_track_index][0], str(int(track_list[old_track_index][1]) + int(new_track.weight)), track_list[old_track_index][2])
                    track_exists = True
                    break
                
            if not track_exists:
                track_list.append((new_track.item,new_track.weight,"False"))
                
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
            

def spotifyConnect():
    username = 'temp user'
    scope = 'playlist-modify-public'
        
    token = util.prompt_for_user_token(username,
                                       scope,
                                       client_id='temp id',
                                       client_secret='temp secret',
                                       redirect_uri='https://open.spotify.com/')
    if token:
        sp = spotipy.Spotify(auth=token)
    return sp

def getPlaylistID(user):
    playlists = user.user_playlists('temp user')
    playlistID = ""
    for playlist in playlists['items']:
        if(playlist['name'] == "Automated Best Of"):
            playlistID = playlist['id']
    return playlistID

def getSpotifyURIs(user, tracks):
    uris = []
    for track in tracks:
        output = user.search(track,limit=1,offset=0,type='track',market=None)
        try:
            uris.append(output["tracks"]["items"][0]["uri"])
            print(track + " found")
        except:
            print("Issue with track " + track)
    return uris

def getNewPlaylistSongs(user, playlistID, offset, new_tracks):
    playlists = user.user_playlists('temp user',limit=50, offset=offset)
    for playlist in playlists['items']:
        if playlist['owner']['id'] == 'temp user' and playlist['id'] != playlistID:
            new_tracks = getSongsFromPlaylist(user, playlist, 0, new_tracks)
    if(len(playlists['items']) == 50):
        getNewPlaylistSongs(user, playlistID, (offset + 50), new_tracks) 
    return new_tracks

def getSongsFromPlaylist(user, playlist, offset, new_tracks):
    tracks = user.user_playlist_tracks('temp user', playlist_id=playlist['id'], fields='items', limit=100, offset=offset)
    print('' + playlist['name'] + ": " + str(len(tracks['items'])))
    for i, item in enumerate(tracks['items']):
        track = item['track']
        new_tracks.append(track['artists'][0]['name'] + ' - ' + track['name'])
    if(len(tracks['items']) == 100):
        getSongsFromPlaylist(user, playlist, (offset + 100), new_tracks)
    return new_tracks

def setPlayListSongsToUpdate(new_tracks):
    track_list = getTrackList()
    print("Length of file before playlist update: " + str(len(track_list)))
    for track in new_tracks:
        track_found = False
        for track_index in range(len(track_list)):
            if track == track_list[track_index][0]:
                track_found = True
                if track_list[track_index][2] == "False":
                    track_list[track_index] = (track_list[track_index][0], "5", track_list[track_index][2])
                break
        if not track_found:
            track_list.append((str(track), "5", "False"))
            
    with open('tracks.txt', 'w+') as file:
        for track in track_list:
            file.write('\n' + str(track[0]) + ";" + str(track[1]) + ";" + str(track[2]))
        file.close()
    print("Length of file after playlist update: " + str(len(track_list)))
    
def addToPlaylist(user, playlistID, urisList):                
    uris = urisList[:100]
    urisList = urisList[100:]
    print(uris)
    user.user_playlist_add_tracks('temp user', playlistID, uris)
    print("Added")
    if len(urisList) != 0:
        time.sleep(1)
        addToPlaylist(user, playlistID, urisList)
        
def main():
    #get last.fm side of things
    updateTrackFile()

    playlist_tracks = getSongsForPlaylist()
    
    user = spotifyConnect()
    print("Spotify Connected")
    playlistID = getPlaylistID(user)
    print("Playlist ID Aquired")
    print(playlistID)
    print(playlist_tracks)
    uris = getSpotifyURIs(user, playlist_tracks)
    print("Song URIS Requested")
    if len(uris) == 0:
        print("No Changes")
    else:
        addToPlaylist(user, playlistID, uris)
        print("Added to Playlists")
        setPlaylistSongsToTrue()
        
    new_tracks = getNewPlaylistSongs(user, playlistID, 0, [])
    for track in new_tracks:
        print(track)
    setPlayListSongsToUpdate(new_tracks)


    playlist_tracks = getSongsForPlaylist()
    uris = getSpotifyURIs(user, playlist_tracks)
    print("Song URIS Requested")
    if len(uris) == 0:
        print("No Changes")
    else:
        addToPlaylist(user, playlistID, uris)
        print("Added to Playlists")
        setPlaylistSongsToTrue()

if __name__ == '__main__':
    main()
