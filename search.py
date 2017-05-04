import spotipy

import spotipy.util as util
import numpy as np

from neural_net import NeuralNet

class Search:
    def __init__(self, query):
        self.genre_map = ["pop", "hip-hop", "metal/rock", "indie/alternative", "classical", "jazz", "r-n-b", "country"]
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
        # token = "BQDgUh4f6qHjBHmuoRRSt07S7Z_98wtK8ImZkmBvcSWj5ItAdpus3xRu1udx7jPhuG2GemnYtUBnb2xJNoS7QEG2jrGknc815NjOI6rmfcDNxf-6LpiceI78MrnydEhWAc5vd8fx7bI"
        token = "BQBUVzk5gnZP-AZSZw8okcUtxeYxys5nZQb5MlKFBYov4XXfwtnN-ukLBm4bb-8IAzLiHw9mTZ_VtKGTaMom0a5hATGiqUiYULguQez8Jjkwln94En_RJNOn-btiAoUijmoZ_Evgw_Q"
        sp = spotipy.Spotify(token)
        # check for errors here 
        first = sp.search(query)['tracks']['items'][0]
        artist_name = first['artists'][0]['name']
        artist_id = first['artists'][0]['id']
        song_name = first['name']
        searchRes = first['uri']

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
                if (temp[0] == 0):
                    if (output[0] > 0.99):
                        result = [self.genre_map[temp[0]], self.genre_map[temp[1]]]
                    else:
                        result = [self.genre_map[temp[1]]]#[self.genre_map[temp[0]], self.genre_map[temp[1]]]
                else:
                    result = [self.genre_map[temp[0]], self.genre_map[temp[1]]]
            else:
                result = [self.genre_map[temp[0]]]

        seed_genres = []
        for genre in result:
            if "metal" in genre:
                seed_genres.append("heavy-metal")
                seed_genres.append("rock")
            elif "indie" in genre:
                seed_genres.append("indie")
                seed_genres.append("alternative")
            else:
                seed_genres.append(genre)

        recommendations = sp.recommendations(seed_genres=seed_genres, seed_artists=[artist_id])
        suggestions = []
        for track in (recommendations['tracks'])[:5]:
            suggestion = {'name':track['name'], 'artist':track['artists'][0]['name']}
            suggestions.append(suggestion)

        return [result, (song_name, artist_name), suggestions]
        # except:
            # print "try again"



