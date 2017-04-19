import spotipy 

import sys
import json
import os
import spotipy.util as util
import csv
import numpy as np

from neural_net import NeuralNet


# export SPOTIPY_CLIENT_ID='3da3c80782214b98bda0a858bccaec0e'
# export SPOTIPY_CLIENT_SECRET='250f2c4858da43029bf11162907f5f5e'
# export SPOTIPY_REDIRECT_URI='https://www.google.com'

# OAUTH TOKEN = BQCMmat8Cy3Bpfe7iuxo36m8jcTQagDxgtx0tLg6wycOH9SRDn2I8456vXpDinJWtOZ0Jnf7p0-Fo6RrgqVv0pdei91F9ESZVa-LEMvG1KgR_rkp2seMCGAOarfocur23WQ_mv9raJ0

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
    subdirectories = os.walk("millionsongdataset_echonest")
    for roots, dirs, files in subdirectories:
        folder = os.walk(roots)
        for r, d, filenames in folder:
            if (r != "millionsongdataset_echonest"):
                for filename in filenames:
                    if (filename[0] != "."):
                        with open(os.path.join(r, filename)) as data_file:  
                            data = json.load(data_file)

                        response = data["response"]
                        songs = response["songs"]
                        if (len(songs) > 0):
                            # database website says only one song per file
                            tracks = songs[0]["tracks"]
                            spotify_found = False
                            for track in tracks:
                                if (track["catalog"] == "spotify"):
                                    foreign_id = (track["foreign_id"]).split(":")
                                    track_ids.append(foreign_id[-1])
                                    spotify_found = True
                                    break

    return track_ids

username = '1259307384'
token = util.prompt_for_user_token(username)
if (token):
    sp = spotipy.Spotify(token)

    # get ids (list of song ids)
    
    track_ids = get_track_ids()
    # print len(track_ids)

    analysis = []
    genres = []

    for i in xrange(0, len(track_ids), 50):
        num = min(50,len(track_ids)-i)
        id_section = track_ids[i:i+num]

        tracks = sp.tracks(id_section)['tracks']

        artist_ids = []
        for track in tracks:
            # some error here->track is none? some id not valid->just filter nones?
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
                genres.append(artist_genre)

            count += 1

        analysis.extend(sp.audio_features(tracks=id_section))

    # print len(genres)
    # print len(analysis)


    input_features = np.empty([len(analysis), 9])
    row = 0

    for analyzed in analysis:
        feature_list = [analyzed['energy'], analyzed['liveness'], analyzed['tempo'], 
                        analyzed['speechiness'], analyzed['acousticness'], 
                        analyzed['instrumentalness'], analyzed['danceability'],
                        analyzed['loudness'], analyzed['valence']]

        input_features[row] = feature_list
        row += 1

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

    