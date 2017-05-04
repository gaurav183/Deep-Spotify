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


def normalize(x, mini, maxi):
    if x==None:
        print "x is None"
    if mini==None:
        print "min is None"
    return (x-mini)/(maxi-mini)
# export SPOTIPY_CLIENT_ID='3da3c80782214b98bda0a858bccaec0e'
# export SPOTIPY_CLIENT_SECRET='250f2c4858da43029bf11162907f5f5e'
# export SPOTIPY_REDIRECT_URI='https://www.google.com'

OAUTH_TOKEN = 'BQCMjTEnwkwv5gtWm_0DFLi6HgmVGYWPt-rdWvgCxtWGvmv9zzQXgO4LOdfqQ-moWkWiiOIvnXhfloVKrKrybDp5myCqbRC5ljmjGTSXaPm2JR8yA8TD27_MljhubF5FEaKCacd2FXY'
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


random.seed(0)
np.random.seed(0)

username = '12180915492'
genre_dict = {}
token = util.prompt_for_user_token(username)
if (token):
    sp = spotipy.Spotify(token)

    analysis = []
    genres = []

    # validIds = []
    spotifySongs = read_spotify_ids();
    # spotifySongs = get_spotify_artist_ids(20, 10)    

    # get ids (list of song ids)
    millionSongs = read_track_ids();

    track_ids = spotifySongs[:10000] + millionSongs[:0]

    numPos = len(track_ids)
    for i in xrange(0, numPos, 50):
        num = min(50,numPos-i)
        id_section = track_ids[i:i+num]

        # try:
        #     tracks = sp.tracks(id_section)['tracks']
        # except:
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
                del id_section[count]
                count -= 1
            else:
                # for genre in artist_genre:
                #     if genre in genre_dict:
                #         genre_dict[genre] +=1
                #     else:
                #         genre_dict[genre] = 1
                genres.append(artist_genre)
            count += 1
        if (len(id_section)!=0):
            analysis.extend(sp.audio_features(tracks=id_section))


    #sorted_x = sorted(genre_dict.items(), key=operator.itemgetter(1))
    #print sorted_x

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
    print len(genres)
    print len(analysis)

    assert(len(genres) == len(analysis))

    print "all good before nones"
    
    numNones = analysis.count(None)
    print "nones ", numNones
    for num in xrange(numNones):
        index = analysis.index(None)
        del genres[index]
        del analysis[index]

    labels = np.zeros([len(genres), 8])
    rowL = 0
    #for genre_list in genres:
    while rowL<len(genres):
        # dummyLabel = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        dummyLabel = [0, 0, 0, 0, 0, 0, 0, 0]
        genre_list = genres[rowL]
        for gen in genre_list:
            if (("pop" in gen)):
                dummyLabel[0] = 1
            if (("teen" in gen)):
                dummyLabel[0] = 1
                # dummyLabel[7] = 1
            # if (("house" in gen) or ("tropical" in gen)):
            #     dummyLabel[1] = 1
            if (("house" in gen) or ("tropical" in gen) or ("edm" in gen)):
                dummyLabel[0] = 1
            # if (("rave" in gen)):
            # #     dummyLabel[1] = 1
            #      dummyLabel[2] = 1
            # if (("edm" in gen) or ("electro" in gen)):
            #     dummyLabel[2] = 1
            if (("rap" in gen) or ("trap" in gen) or ("hip hop" in gen)):
                dummyLabel[1] = 1
                # dummyLabel[0] = 1
            if (("metal" in gen) or ("grunge" in gen) or ("emo" in gen)):
                dummyLabel[2] = 1
                # dummyLabel[1] = 1
            if (("indie" in gen) or ("folk" in gen) or ("alternative" in gen)):
                dummyLabel[3] = 1
                # dummyLabel[2] = 1
            if (("classical" in gen) or ("romantic" in gen)):
                dummyLabel[4] = 1
                # dummyLabel[3] = 1
            if (("jazz" in gen) or ("blues" in gen) or ("soul" in gen)):
                dummyLabel[5] = 1
                # dummyLabel[4] = 1
            if (("r&b" in gen)):
                dummyLabel[6] = 1
                # dummyLabel[5] = 1
            if (("dance" in gen) or ("punk" in gen)):
                # dummyLabel[7] = 1
                # dummyLabel[6] = 1
                dummyLabel[0] = 1
            if ("rock" in gen):
                # dummyLabel[8] = 1
                dummyLabel[2] = 1
                # dummyLabel[6] = 1
            if (("country" in gen) or ("southern" in gen)):
                # dummyLabel[9] = 1
                # dummyLabel[8] = 1
                dummyLabel[7] = 1
        
        if (1 not in dummyLabel):
            del analysis[rowL]
            labels = np.delete(labels, rowL, 0)
            del genres[rowL]
        else: 
            labels[rowL] = dummyLabel
            rowL += 1
    
    print "all good, both are ", len(analysis)


#HERE
    input_features = np.zeros([len(analysis), 10])
    # input_features = np.zeros([len(analysis), 9])
    
#HERE
    keys = ['energy', 'liveness', 'tempo', 'speechiness', 'acousticness', 'instrumentalness', 'danceability', 'loudness', 'valence', 'mode']
    # keys = ['energy', 'liveness', 'tempo', 'speechiness', 'acousticness', 'danceability', 'loudness', 'valence']
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
    print len(analysis)
    for analyzed in analysis:
        feature_list = []
        for key in keys:
            if analyzed[key]==None:
                # double check this
                del genres[rowI]
                labels = np.delete(labels, rowI, 0)
                break
            v = normalize(analyzed[key], min_values[key], max_values[key])
            feature_list.append(v)

#HERE
        if len(feature_list)==10:
        # if len(feature_list)==9:
            input_features[rowI] = feature_list
            rowI += 1
    # print rowI
    while rowI<(input_features.shape)[0]:
        input_features = np.delete(input_features, rowI, 0)

    # print "input = ", input_features
    #print "labels = ", labels
    #print "genres =", genres
    print len(labels)
    print len(input_features)
    print len(genres)

    # call NN with input_features
    learning_rate = 0.3

#HERE
    # structure = {'num_inputs': 10, 'num_hidden': 30, 'num_outputs': 10}
    structure = {'num_inputs': 10, 'num_hidden': 30, 'num_outputs': 8}
    candidate = NeuralNet(structure, learning_rate)

    #iterations = 15000
    iterations = 200

    candidate.train(input_features, labels, iterations)

    #cand_error = candidate.test(input_features, labels)
    #print "Train error: ", cand_error

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
    # why isnt there a None
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

    


    
