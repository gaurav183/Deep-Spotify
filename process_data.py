import spotipy

import sys
import json
import os
import spotipy.util as util
import csv
import numpy as np
import operator

from neural_net import NeuralNet


# export SPOTIPY_CLIENT_ID='3da3c80782214b98bda0a858bccaec0e'
# export SPOTIPY_CLIENT_SECRET='250f2c4858da43029bf11162907f5f5e'
# export SPOTIPY_REDIRECT_URI='https://www.google.com'

OAUTH_TOKEN = 'BQCMjTEnwkwv5gtWm_0DFLi6HgmVGYWPt-rdWvgCxtWGvmv9zzQXgO4LOdfqQ-moWkWiiOIvnXhfloVKrKrybDp5myCqbRC5ljmjGTSXaPm2JR8yA8TD27_MljhubF5FEaKCacd2FXY'
def get_spotify_artist_ids():
    artist_ids = []
    categories = sp.categories()["categories"]
    items = categories["items"]
    for item in items[:15]:
        cat_id = item["id"]
        playlists = sp.category_playlists(cat_id)["playlists"]
        for playlist in playlists["items"][:10]:
            user = playlist["owner"]["id"]
            playlist_id = (playlist["uri"].split(":"))[-1]
            user_playlist = sp.user_playlist_tracks(user, playlist_id)
            tracks = user_playlist["items"]
            for track in tracks:
                try:
                    artists = track["track"]["artists"]
                    artist_ids.append((artists[0]["uri"].split(":"))[-1])
                except:
                    pass
    return artist_ids



def get_track_ids():
    track_ids = []
    # top 200 songs from spotify charts
    with open('regional-global-daily-latest.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row['URL']
            url_list = url.split("/")
            track_ids.append(url_list[-1])
      
    # one million songs from echonest song dataset 
    # subdirectories = os.walk("millionsongdataset_echonest")
    # for roots, dirs, files in subdirectories:
    #     folder = os.walk(roots)
    #     for r, d, filenames in folder:
    #         if (r != "millionsongdataset_echonest"):
    #             for filename in filenames:
    #                 if len(track_ids)>1000:
    #                     return track_ids
    #                 if (filename[0] != "."):
    #                     with open(os.path.join(r, filename)) as data_file:  
    #                         data = json.load(data_file)

    #                     response = data["response"]
    #                     songs = response["songs"]
    #                     if (len(songs) > 0):
    #                         # database website says only one song per file
    #                         tracks = songs[0]["tracks"]
    #                         spotify_found = False
    #                         for track in tracks:
    #                             if (track["catalog"] == "spotify"):
    #                                 foreign_id = (track["foreign_id"]).split(":")
    #                                 track_ids.append(foreign_id[-1])
    #                                 spotify_found = True
    #                                 break

    return track_ids

username = '12180915492'
genre_dict = {}
token = True
#token = util.prompt_for_user_token(username)
if (token):
    sp = spotipy.Spotify(OAUTH_TOKEN)

    # get ids (list of song ids)
    
    track_ids = get_track_ids()


    analysis = []
    genres = []

    # validIds = []
    temp_artist_ids = get_spotify_artist_ids()
    
    for i in xrange(0, len(temp_artist_ids), 50):
        num = min(50,len(temp_artist_ids)-i)
        id_section = temp_artist_ids[i:i+num]
        artists = sp.artists(id_section)['artists']
        count = 0
        for artist in artists:
            artist_genre = artist['genres']
            if (len(artist_genre)==0):
                #assert(len(sp.artist((sp.track(id_section[count]))['artists'][0]['uri'])['genres'])==0)
                del id_section[count]
                count -= 1
            else:
                for genre in artist_genre:
                    if genre in genre_dict:
                        genre_dict[genre] +=1
                    else:
                        genre_dict[genre] = 1
                genres.append(artist_genre)

            count += 1

        analysis.extend(sp.audio_features(tracks=id_section))


    for i in xrange(0, len(track_ids), 50):
        num = min(50,len(track_ids)-i)
        id_section = track_ids[i:i+num]

        tracks = sp.tracks(id_section)['tracks']

        numNones = tracks.count(None)
        for num in xrange(numNones):
            index = tracks.index(None)
            del id_section[index]
            del tracks[index]

        # validIds.extend(id_section)

        artist_ids = []
        for track in tracks:
            artist_ids.append(track['artists'][0]['uri'])
                
        artists = sp.artists(artist_ids)['artists']




        count = 0
        for artist in artists:
            artist_genre = artist['genres']
            if (len(artist_genre)==0):
                #assert(len(sp.artist((sp.track(id_section[count]))['artists'][0]['uri'])['genres'])==0)
                del id_section[count]
                count -= 1
            else:
                for genre in artist_genre:
                    if genre in genre_dict:
                        genre_dict[genre] +=1
                    else:
                        genre_dict[genre] = 1
                genres.append(artist_genre)

            count += 1

        analysis.extend(sp.audio_features(tracks=id_section))

    # with open('song_ids.txt') as thefile:
    #     print "writing"
    #     for id in validIds:
    #         thefile.write("%s\n" % id)

    sorted_x = sorted(genre_dict.items(), key=operator.itemgetter(1))
    #print sorted_x


    # input_features = np.empty([len(analysis), 9])
    # row = 0

    # for analyzed in analysis:
    #     feature_list = [analyzed['energy'], analyzed['liveness'], analyzed['tempo'], 
    #                     analyzed['speechiness'], analyzed['acousticness'], 
    #                     analyzed['instrumentalness'], analyzed['danceability'],
    #                     analyzed['loudness'], analyzed['valence']]

    #     input_features[row] = feature_list
    #     row += 1


    # call NN with input_features
    # learning_rate = 0.5
    # structure = {'num_inputs': 9, 'num_hidden': 5, 'num_outputs': 10}
    # candidate = NeuralNet(structure, learning_rate)

    # #iterations = 15000
    # iterations = 20

    # candidate.train(input_features, labels, iterations)

    # cand_error = candidate.test(input_features, labels)
    # print "Train fraction: ", cand_error
          
else:
    print("Can't get token for", username)

    
