import spotipy

import sys
import json
import os
import spotipy.util as util
import csv
import numpy as np
import operator
import random

from neural_net import NeuralNet


# export SPOTIPY_CLIENT_ID='3da3c80782214b98bda0a858bccaec0e'
# export SPOTIPY_CLIENT_SECRET='250f2c4858da43029bf11162907f5f5e'
# export SPOTIPY_REDIRECT_URI='https://www.google.com'
OAUTH_TOKEN = 'BQCMjTEnwkwv5gtWm_0DFLi6HgmVGYWPt-rdWvgCxtWGvmv9zzQXgO4LOdfqQ-moWkWiiOIvnXhfloVKrKrybDp5myCqbRC5ljmjGTSXaPm2JR8yA8TD27_MljhubF5FEaKCacd2FXY'

random.seed(0)
np.random.seed(0)

username = '12180915492'
genre_dict = {}
token = util.prompt_for_user_token(username)

def normalize(x, mini, maxi):
    if x==None:
        print "x is None"
    if mini==None:
        print "min is None"
    return (x-mini)/(maxi-mini)


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


def read_track_ids():
    with open('song_ids.txt') as idsFile:
        track_ids = [x.strip('\n') for x in idsFile.readlines()]

    return track_ids

def read_spotify_ids():
    with open('spotify_ids.txt') as idsFile:
        songs = [x.strip('\n') for x in idsFile.readlines()]

    return songs


def generateData(track_ids):
    analysis = []
    genres = []

    numPos = len(track_ids)
    for i in xrange(0, numPos, 50):
        num = min(50,numPos-i)
        id_section = track_ids[i:i+num]

        
        token = util.prompt_for_user_token(username)
        sp = spotipy.Spotify(token)
        tracks = sp.tracks(id_section)['tracks']


        artist_ids = []
        for track in tracks:
            artist_ids.append(track['artists'][0]['uri'])
                
        artists = sp.artists(artist_ids)['artists']


        count = 0
        for artist in artists:
            artist_genre = artist['genres']
            
            if (len(artist_genre)==0):
                del id_section[count]
                count -= 1
            else:
                genres.append(artist_genre)

            count += 1

        if (len(id_section) != 0):
            analysis.extend(sp.audio_features(tracks=id_section))

    print "data"
    print len(genres)
    print len(analysis)
    assert (len(genres)==len(analysis))
    return (genres, analysis)

def removeNones(genres, analysis):
    numNones = analysis.count(None)

    for num in xrange(numNones):
        index = analysis.index(None)
        del genres[index]
        del analysis[index]

    print "nones"
    print len(genres)
    print len(analysis)
    assert (len(genres)==len(analysis))


def getLabels(genres, analysis):
    labels = np.zeros([len(genres), 8])
    rowL = 0

    while rowL<len(genres):
        dummyLabel = [0, 0, 0, 0, 0, 0, 0, 0]
        genre_list = genres[rowL]
        for gen in genre_list:
            if (("pop" in gen) or ("dance" in gen) or ("punk" in gen) or ("teen" in gen)):
                dummyLabel[0] = 1

            if (("house" in gen) or ("tropical" in gen) or ("edm" in gen)):
                dummyLabel[0] = 1

            if (("rap" in gen) or ("trap" in gen) or ("hip hop" in gen)):
                dummyLabel[1] = 1

            if (("metal" in gen) or ("grunge" in gen) or ("emo" in gen) or ("rock" in gen)):
                dummyLabel[2] = 1

            if (("indie" in gen) or ("folk" in gen) or ("alternative" in gen)):
                dummyLabel[3] = 1

            if (("classical" in gen) or ("romantic" in gen)):
                dummyLabel[4] = 1

            if (("jazz" in gen) or ("blues" in gen) or ("soul" in gen)):
                dummyLabel[5] = 1

            if (("r&b" in gen)):
                dummyLabel[6] = 1

            if (("country" in gen) or ("southern" in gen)):
                dummyLabel[7] = 1
        
        if (1 not in dummyLabel):
            del analysis[rowL]
            labels = np.delete(labels, rowL, 0)
            del genres[rowL]
        else: 
            labels[rowL] = dummyLabel
            rowL += 1
    

    print "labels"
    print len(genres)
    print len(analysis)
    assert (len(genres)==len(analysis))
    return labels

def getInput(genres, analysis, labels):
    input_features = np.zeros([len(analysis), 10])
    

    keys = ['energy', 'liveness', 'tempo', 'speechiness', 'acousticness', 'instrumentalness', 'danceability', 'loudness', 'valence', 'mode']

    values = {}
    min_values = {}
    max_values = {}
    for analyzed in analysis: 
        for key in keys:
            if analyzed[key]!=None:
                if key not in values:
                    values[key] = []
                values[key].append(analyzed[key])
    for key in values:
        min_values[key] = min(values[key])
        max_values[key] = max(values[key])


    np.save('min_vals.npy', min_values)
    np.save('max_vals.npy', max_values)

    rowI = 0

    for analyzed in analysis:
        feature_list = []
        for key in keys:
            if analyzed[key]==None:
                del genres[rowI]
                labels = np.delete(labels, rowI, 0)
                break

            v = normalize(analyzed[key], min_values[key], max_values[key])
            feature_list.append(v)

        if len(feature_list)==10:
            input_features[rowI] = feature_list
            rowI += 1

    while rowI<(input_features.shape)[0]:
        input_features = np.delete(input_features, rowI, 0)


    return input_features


if (token):
    sp = spotipy.Spotify(token)

    # get ids from 
    spotifySongs = read_spotify_ids();

    # get ids from million song dataset
    millionSongs = read_track_ids();

    track_ids1 = spotifySongs[0:12000] + millionSongs[:0]
    track_ids2 = spotifySongs[10000:22000] + millionSongs[:0]

    (genres1, analysis1) = generateData(track_ids1)

    (genres2, analysis2) = generateData(track_ids2)


    # print len(genres)
    # print len(analysis)

    # assert(len(genres) == len(analysis))

    # print "all good before nones"
    
    removeNones(genres1, analysis1)
    removeNones(genres2, analysis2)


    labels1 = getLabels(genres1, analysis1)
    labels2 = getLabels(genres2, analysis2)


    input_features1 = getInput(genres1, analysis1, labels1)
    input_features2 = getInput(genres2, analysis2, labels2)

    # print len(labels)
    # print len(input_features)
    # print len(genres)

    # call NN with input_features
    learning_rate = 0.3

    for h in xrange(6):
        structure = {'num_inputs': 10, 'num_hidden': 5*(h+1), 'num_outputs': 8}
        candidate = NeuralNet(structure, learning_rate)

        iterations = 125

        candidate.train(input_features1, labels1, iterations)

        cand_error1 = candidate.test(input_features1, labels1, 0)
        cand_error2 = candidate.test(input_features2, labels2, 0)

        print "h = ", (h+1), " Train error: ", cand_error1, " Test error: ", cand_error2


    keys = ['energy', 'liveness', 'tempo', 'speechiness', 'acousticness', 'instrumentalness', 'danceability', 'loudness', 'valence', 'mode']

    # sorry (bieber), closer, shape of you
    popTestTracks = ["09CtPGIpYB4BrO8qb1RGsF", "7BKLCZ1jbUBVqRi2FVlTVw", "0FE9t6xYkqWXU2ahLh6D8X"]
    # moonlight sonata, clair de lune, canon in D
    classicalTestTracks  = ["3DNRdudZ2SstnDCVKFdXxG", "4H4KkHfXJs3cQEnbNW3bVS", "6A6vSsLkXoTJZ8cA4vtznl"]
    # HUMBLE, fake love, mask off
    rapTestTracks = ["7KXjTSCq5nL1LoYtL7XAwS", "343YBumqHu19cGoGARUTsd", "3rOSwuTsUlJp0Pu0MkN8r8"]
    # enter sandman, man in the box, iron man (might show rock)
    metalTestTracks = ["1hKdDCpiI9mqz1jVHRKG0E", "6gZVQvQZOFpzIy3HblJ20F","3IOQZRcEkplCXg6LofKqE9"]
    # beautiful day, smells like teen spirit (might show metal)
    rockTestTracks = ["1VuBmEauSZywQVtqbxNqka", "5ghIJDpPoe3CfHMGu71E6T"]

    jazzTestTracks = ["4Vqa8U8soMx9yT2HtoWXUY", "1AwBPJOJuyAxIBKyhg153s", "5p6me2mwQrGfH30eExHn6v"]

    testTracks = popTestTracks + classicalTestTracks + rapTestTracks + metalTestTracks + rockTestTracks + jazzTestTracks
    testAnalysis = sp.audio_features(tracks=testTracks)
    
    testInput = np.zeros([len(testTracks), 10])

    count = 0

    min_values = np.load('min_vals.npy')
    max_values = np.load('max_vals.npy')

    for analyzed in testAnalysis:
        testFeature = []
        for key in keys:
            if (key!='mode'):
                v = normalize(analyzed[key], min_values[key], max_values[key])
            else:
                v = analyzed[key]

            testFeature.append(v)

        testInput[count] = testFeature
        count += 1


    for i in xrange(len(testTracks)):
        output = candidate.forward_propagate(testInput[i], 1)
        temp = [j[0] for j in sorted(enumerate(output), key=lambda x:x[1])]
        temp.reverse()
        if output[temp[1]]>0.5:
            print temp[0], temp[1]
        else:
            print temp[0]
        print testTracks[i]
          
else:
    print("Can't get token for", username)


