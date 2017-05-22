# Deep Spotify

https://youtu.be/AKWStTfWewU

pip install Flask

navigate into FlaskApp folder and run python app.py and go to localhost:5000 in your browser

follow steps to authenticate your Spotify account

input any song and watch it predict the genre!

create_spotify_file.py-Stores track_ids using Spotipy

genres.txt-Uses .txt file to store genres that categorize songs

max_vals.npy-Dictionary that stores max values of each acoustic feature when they are all normalized

min_vals.npy-Dictionary that stores min values of each acoustic feature when they are all normalized

neural_net.py-Contains neural network used to categorize each song in genre(s)

process_data.py-Get track_ids from songs using Spotipy, creates labels, normalizes acoustic features found using Spotipy, passes data through neural network

saved_w1.npy-Numpy array that stores weights of nodes from input layer to hidden layer

saved_w2.npy-Numpy array that stores weights of nodes from input layer to hidden layer

search.py-Takes query and uses neural network to output genre predictions and track recommendations

song_ids.txt-Contains dataset of one million songs

spotify_ids.txt-Contains dataset of songs from featured playlists on spotify

