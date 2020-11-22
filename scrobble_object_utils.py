def check_for_unwanted_characters(track_object):
    track_object.track_artist = track_object.track_artist.replace("…", "...")
    track_object.track_artist = track_object.track_artist.replace("’", "'")
    track_object.track_name = track_object.track_name.replace("…", "...")
    track_object.track_name = track_object.track_name.replace("’", "'")
