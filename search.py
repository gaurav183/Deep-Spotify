import spotipy

import spotipy.util as util
import numpy as np

from neural_net import NeuralNet

class Search:
    def __init__(self, query):
        self.genre_map = ["pop", "hip hop", "metal/rock", "indie", "classical", "jazz", "r&b", "country"]
        self.query = query

    def run(self):
        return self.predict(self.query)

    def normalize(self, x, mini, maxi):
        if x==None:
            print "x is None"
        if mini==None:
            print "min is None"
        return (x-mini)/(maxi-mini)

    def predict(self, query):

        # try:
        username = '12180915492'
        #token = util.prompt_for_user_token(username)
        # change this back 
        token = "BQDgUh4f6qHjBHmuoRRSt07S7Z_98wtK8ImZkmBvcSWj5ItAdpus3xRu1udx7jPhuG2GemnYtUBnb2xJNoS7QEG2jrGknc815NjOI6rmfcDNxf-6LpiceI78MrnydEhWAc5vd8fx7bI"
        sp = spotipy.Spotify(token)
        # check for errors here 
        searchRes = sp.search(query)['tracks']['items'][0]['uri']

        # call NN with input_features

        structure = {'num_inputs': 10, 'num_hidden': 30, 'num_outputs': 8}
        learning_rate = 0.3
        candidate = NeuralNet(structure, learning_rate)

        keys = ['energy', 'liveness', 'tempo', 'speechiness', 'acousticness', 'instrumentalness', 'danceability', 'loudness', 'valence', 'mode']

        min_vals = np.load('min_vals.npy').item()
        max_vals = np.load('max_vals.npy').item()

        testTracks = [searchRes]
        testAnalysis = sp.audio_features(tracks=testTracks)
        if testAnalysis==None:
            return ["Oops, Spotify doesn't recognize that song"]

        testInput = np.zeros([len(testTracks), 10])

        rowI = 0


        for analyzed in testAnalysis:
            feature_list = []
            for key in keys:
                if analyzed[key]==None:
                    break
                v = self.normalize(analyzed[key], min_vals[key], max_vals[key])
                feature_list.append(v)
            if len(feature_list)==10:
                testInput[rowI] = feature_list
                rowI += 1

        while rowI<(testInput.shape)[0]:
            testInput = np.delete(testInput, rowI, 0)
        if len(testInput)==0:
            return ["Oops, we don't recognize that song"]
        result = None
        for i in xrange(len(testTracks)):
            output = candidate.forward_propagate(testInput[i], 1)
            temp = [j[0] for j in sorted(enumerate(output), key=lambda x:x[1])]
            temp.reverse()
            if output[temp[1]]>0.5:
                result = [self.genre_map[temp[0]], self.genre_map[temp[1]]]
            else:
                result = [self.genre_map[temp[0]]]
        return result

        # except:
            # print "try again"



