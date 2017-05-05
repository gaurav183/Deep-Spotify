# Deep-Spotify

pip install Flask

navigate into FlaskApp folder and run python app.py and go to localhost:5000 in your browser

follow steps to authenticate your Spotify account

input any song and watch it predict the genre!

create_spotify_file.py

Stores track_ids using Spotipy

genres.txt

Uses .txt file to store genres that categorize songs

max_vals.npy

Dictionary that stores max values of each acoustic feature when they are all normalized

min_vals.npy

Dictionary that stores min values of each acoustic feature when they are all normalized

neural_net.py

Neural network used to categorize each song in a genre

process_data.py

Get track_ids from songs using Spotipy, creates labels, normalizes acoustic features found using Spotipy, passes data through neural network
