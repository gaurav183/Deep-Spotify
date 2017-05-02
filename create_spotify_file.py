import spotipy

import sys
import json
import os
import spotipy.util as util
import csv
import numpy as np
import operator

def get_spotify_artist_ids(numCats, numPlays):
    artist_ids = []
    track_ids = []
    categories = sp.categories()["categories"]
    items = categories["items"]
    actualNumCats = max(numCats, len(items))
    for item in items[:actualNumCats]:
        cat_id = item["id"]
        playlists = sp.category_playlists(cat_id)["playlists"]
        actualNumPlays = max(numPlays, len(playlists["items"]))
        for playlist in playlists["items"][:actualNumPlays]:
            user = playlist["owner"]["id"]
            playlist_id = (playlist["uri"].split(":"))[-1]
            user_playlist = sp.user_playlist_tracks(user, playlist_id)
            tracks = user_playlist["items"]
            for track in tracks:
                try:
                    artists = track["track"]["artists"]
                    artist_ids.append((artists[0]["uri"].split(":"))[-1])
                    track_ids.append(track['track']['id'])
                except:
                    pass

    return track_ids

username = '12180915492'
genre_dict = {}
token = util.prompt_for_user_token(username)
if (token):
    sp = spotipy.Spotify(token)

    songs = get_spotify_artist_ids(100, 100)
    print len(songs)
    with open('spotify_ids.txt', 'w') as thefile:
        print "writing"
        for id in songs:
            thefile.write("%s\n" % id)

