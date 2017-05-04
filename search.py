import spotipy

import spotipy.util as util
import numpy as np

from neural_net import NeuralNet

def normalize(x, mini, maxi):
    if x==None:
        print "x is None"
    if mini==None:
        print "min is None"
    return (x-mini)/(maxi-mini)

def predict(query):

    # try:
    username = '12180915492'
    token = util.prompt_for_user_token(username)
    sp = spotipy.Spotify(token)
    searchRes = sp.search(query)['tracks']['items'][0]['uri']

    # call NN with input_features

    structure = {'num_inputs': 10, 'num_hidden': 30, 'num_outputs': 8}
    learning_rate = 0.3
    candidate = NeuralNet(structure, learning_rate)

    keys = ['energy', 'liveness', 'tempo', 'speechiness', 'acousticness', 'instrumentalness', 'danceability', 'loudness', 'valence', 'mode']

    testTracks = [searchRes]
    testAnalysis = sp.audio_features(tracks=testTracks)
    testVals = {}
    testMin = {}
    testMax = {}
    testInput = np.zeros([len(testTracks), 10])

    for analyzed in testAnalysis:
        for key in keys:
            if analyzed[key]!=None:
                if key not in testVals:
                    testVals[key] = []
                testVals[key].append(analyzed[key])
    for key in testVals:
        testMin[key] = min(testVals[key])
        testMax[key] = max(testVals[key])

    count = 0
    for analyzed in testAnalysis:
        testFeature = []
        for key in keys:
            if (key=='mode'):
                v = normalize(analyzed[key], testMin[key], testMax[key])
            else:
                v = analyzed[key]

            testFeature.append(v)

        testInput[count] = testFeature
        count += 1

    for i in xrange(len(testTracks)):
        output = candidate.forward_propagate(testInput[i], 1)

        print testTracks[i], " ----> ", output

    # except:
        # print "try again"



if __name__ == "__main__":
    predict("Humble")
