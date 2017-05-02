import spotipy

import sys
import json
import os
import spotipy.util as util
import csv
import numpy as np
import operator

from neural_net import NeuralNet

def normalize(x, mini, maxi):
    return (x-mini)/(maxi-mini)
# export SPOTIPY_CLIENT_ID='3da3c80782214b98bda0a858bccaec0e'
# export SPOTIPY_CLIENT_SECRET='250f2c4858da43029bf11162907f5f5e'
# export SPOTIPY_REDIRECT_URI='https://www.google.com'

OAUTH_TOKEN = 'BQCMjTEnwkwv5gtWm_0DFLi6HgmVGYWPt-rdWvgCxtWGvmv9zzQXgO4LOdfqQ-moWkWiiOIvnXhfloVKrKrybDp5myCqbRC5ljmjGTSXaPm2JR8yA8TD27_MljhubF5FEaKCacd2FXY'
def get_spotify_artist_ids(numCats, numPlays):
    artist_ids = []
    categories = sp.categories()["categories"]
    items = categories["items"]
    for item in items[:numCats]:
        cat_id = item["id"]
        playlists = sp.category_playlists(cat_id)["playlists"]
        for playlist in playlists["items"][:numPlays]:
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




def read_track_ids():
    with open('song_ids.txt') as idsFile:
        track_ids = [x.strip('\n') for x in idsFile.readlines()]

    return track_ids


username = '12180915492'
genre_dict = {}
token = util.prompt_for_user_token(username)
if (token):
    sp = spotipy.Spotify(token)

    analysis = []
    genres = []

    # validIds = []
    featured_artist_ids = get_spotify_artist_ids(20, 10)
    
    numCats = 500
    for i in xrange(0, numCats, 50):
        num = min(50,numCats-i)
        id_section = featured_artist_ids[i:i+num]

        try:
            artists = sp.artists(id_section)['artists']
        except:
            token = util.prompt_for_user_token(username)
            sp = spotipy.Spotify(token)
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


    # get ids (list of song ids)
    track_ids = read_track_ids();

    numPos = 1000
    for i in xrange(0, numPos, 50):
        num = min(50,numPos-i)
        id_section = track_ids[i:i+num]

        try:
            tracks = sp.tracks(id_section)['tracks']
        except:
            token = util.prompt_for_user_token(username)
            sp = spotipy.Spotify(token)
            tracks = sp.tracks(id_section)['tracks']


        # numNones = tracks.count(None)
        # for num in xrange(numNones):
        #     index = tracks.index(None)
        #     del id_section[index]
        #     del tracks[index]

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

    # sorted_x = sorted(genre_dict.items(), key=operator.itemgetter(1))
    # print sorted_x

    """
    pop - {teen}
    house - {tropical, rave}
    edm - {electro, rave}
    rap - {trap, hip, hop, grime}
    metal - {grunge, emo}
    indie - {folk, alternative}
    classical - {romantic}
    jazz - {blues, soul}
    r&b - 
    dance - {punk, teen}
    rock - 
    country - {southern}
    """

    assert(len(genres) == len(analysis))
    
    numNones = analysis.count(None)
    print len(analysis)
    print numNones
    for num in xrange(numNones):
        index = analysis.index(None)
        del genres[index]
        del analysis[index]

    labels = np.zeros([len(genres), 12])
    rowL = 0
    
    #for genre_list in genres:
    while rowL<len(genres):
        dummyLabel = [0,0,0,0,0,0,0,0,0,0,0,0]
        genre_list = genres[rowL]
        for gen in genre_list:
            if (("pop" in gen)):
                dummyLabel[0] = 1
            if (("teen" in gen)):
                dummyLabel[0] = 1
                dummyLabel[9] = 1
            if (("house" in gen) or ("tropical" in gen)):
                dummyLabel[1] = 1
            if (("rave" in gen)):
                dummyLabel[1] = 1
                dummyLabel[2] = 1
            if (("edm" in gen) or ("electro" in gen)):
                dummyLabel[2] = 1
            if (("rap" in gen) or ("trap" in gen) or ("hip" in gen) or ("hop" in gen) or ("grime" in gen)):
                dummyLabel[3] = 1
            if (("metal" in gen) or ("grunge" in gen) or ("emo" in gen)):
                dummyLabel[4] = 1
            if (("indie" in gen) or ("folk" in gen) or ("alternative" in gen)):
                dummyLabel[5] = 1
            if (("classical" in gen) or ("romantic" in gen)):
                dummyLabel[6] = 1
            if (("jazz" in gen) or ("blues" in gen) or ("soul" in gen)):
                dummyLabel[7] = 1
            if (("r&b" in gen)):
                dummyLabel[8] = 1
            if (("dance" in gen) or ("punk" in gen)):
                dummyLabel[9] = 1
            if ("rock" in gen):
                dummyLabel[10] = 1
            if (("country" in gen) or ("southern" in gen)):
                dummyLabel[11] = 1
        
        if (1 not in dummyLabel):
            del analysis[rowL]
            labels = np.delete(labels, rowL, 0)
            del genres[rowL]
        else: 
            labels[rowL] = dummyLabel
            rowL += 1
    
    print "all good, both are ", len(analysis)

    input_features = np.zeros([len(analysis), 9])
    rowI = 0

    keys = ['energy', 'liveness', 'tempo', 'speechiness', 'acousticness', 'instrumentalness', 'danceability', 'loudness', 'valence']
    values = {}
    min_values = {}
    max_values = {}
    for analyzed in analysis: 
        for key in keys:
            if key not in values:
                values[key] = []
            values[key].append(analyzed[key])
    for key in values:
        min_values[key] = min(values[key])
        max_values[key] = max(values[key])



    for analyzed in analysis:
        feature_list = []
        for key in keys:
            v = normalize(analyzed[key], min_values[key], max_values[key])
            feature_list.append(v)
        # feature_list = [normalize(analyzed['energy'], analyzed['liveness'], analyzed['tempo'], 
        #                 analyzed['speechiness'], analyzed['acousticness'], 
        #                 analyzed['instrumentalness'], analyzed['danceability'],
        #                 abs(analyzed['loudness']), analyzed['valence']]

        input_features[rowI] = feature_list
        rowI += 1

    print "input = ", input_features
    #print "labels = ", labels
    #print "genres =", genres
    print len(genres)

    # call NN with input_features
    learning_rate = 0.2
    structure = {'num_inputs': 9, 'num_hidden': 30, 'num_outputs': 12}
    candidate = NeuralNet(structure, learning_rate)

    #iterations = 15000
    iterations = 50

    candidate.train(input_features, labels, iterations)

    cand_error = candidate.test(input_features, labels)
    print "Train fraction: ", cand_error
          
else:
    print("Can't get token for", username)

    
