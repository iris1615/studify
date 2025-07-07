import requests
import urllib.parse
import os

from flask import Flask, redirect, jsonify, session, request, render_template
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'random aah string'

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

spotify_genres = {
    1: {"genre": "pop",        "color": "#FFB3BA"},
    2: {"genre": "hip hop",    "color": "#FFDFBA"},
    3: {"genre": "rock",       "color": "#BAE1FF"},
    4: {"genre": "rap",        "color": "#D5AAFF"},
    5: {"genre": "indie",      "color": "#C2F0C2"},
    6: {"genre": "dance",      "color": "#FFFACD"},
    7: {"genre": "edm",        "color": "#C9E4DE"},
    8: {"genre": "r&b",        "color": "#DCC6E0"},
    9: {"genre": "soul",       "color": "#FFD6E0"},
    10: {"genre": "jazz",      "color": "#BFD8B8"},
    11: {"genre": "blues",     "color": "#A3C4F3"},
    12: {"genre": "country",   "color": "#FEE1E8"},
    13: {"genre": "classical", "color": "#EAD7D1"},
    14: {"genre": "reggae",    "color": "#C5FAD5"},
    15: {"genre": "latin",     "color": "#FAD6A5"},
    16: {"genre": "k-pop",     "color": "#FFCCE5"},
    17: {"genre": "metal",     "color": "#DAD4EF"},
    18: {"genre": "punk",      "color": "#F7C8E0"},
    19: {"genre": "japanese",      "color": "#E6DDC4"},
    20: {"genre": "funk",      "color": "#FFDEA9"},
    21: {"genre": "house",     "color": "#A0E7E5"},
    22: {"genre": "techno",    "color": "#D0C4DF"},
    23: {"genre": "soundtrack",    "color": "#D0F4DE"},
    24: {"genre": "dubstep",   "color": "#E2CFEA"},
    25: {"genre": "hyperpop",   "color": "#DEFDE0"},
    26: {"genre": "argentine",     "color": "#C3FBD8"},
    27: {"genre": "afrobeats", "color": "#FFE0AC"},
    28: {"genre": "portuguese","color": "#CDE7BE"},
    29: {"genre": "disco",     "color": "#FFF5BA"},
    30: {"genre": "alternative","color": "#D6E2E9"}
}




@app.route('/')
def index():
    return "Welcome to my spotify app !! <a href='/login'>Login with spotify</a>"

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-top-read' # para acedermos aos top-artists precisamos da permissão 'user-top-read'

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True # forçar user a dar login - DEBUGGING,, podemos omitir
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)

@app.route('/callback') # no caso de recebermos um erro
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data= req_body) # o que vamos mandar para o spotify
        token_info = response.json()

        session['access_token'] = token_info['access_token'] # para requests
        session['refresh_token'] = token_info['refresh_token'] # para dar refresh ao access token (apenas dura 1 dia)
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in'] # indica quanto tempo o access_token dura
        
        return redirect('/top-artists') # vai retornar as playlists do user

@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session['expires_at']:
        print("TOKEN EXPIRED,, REFRESHING..")
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    playlists = response.json()

    playlist_names = [playlist['name'] for playlist in playlists['items']]

    return jsonify(playlist_names)

@app.route('/top-artists')
def get_topArtists():
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session['expires_at']:
        print("TOKEN EXPIRED,, REFRESHING..")
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    response = requests.get(API_BASE_URL + 'me/top/artists?time_range=short_term', headers=headers)

    top_artists = response.json()
    #artist_names = [artist['name'] for artist in top_artists['items']]
    #artist_images = [artist['images'] for artist in top_artists['items']]
    artists_data = []
    top_tracks_info = getTopTracksFromTopArtists()
    
    for artist in top_artists['items']:
        artist_info = {
            'name': artist['name'],
            'image_url': artist['images'][0]['url'] if artist['images'] else None,  # Primeira imagem (maior)
            'popularity': artist['popularity'],
            'followers': artist['followers']['total'],
            'external_url': artist['external_urls']['spotify'],
            'tracks': [],
            'genres': artist['genres'], # TODO: no caso de não ter genre vamos fazer uma in terpolação baseada nos genres dos seus related artists, def get_related_artists
            # a interpolação baseada nos géneros dos related-artists não é possível com a api do spotify :(
            'color': "#8D99AE"
        }
        
        for track in top_tracks_info:
            if track['artist'] == artist_info['name']:
                artist_info['tracks'].append(track['name'])

        if artist['genres'] and len(artist['genres']) > 0:
            # Procurar uma cor baseada nos géneros do artista
            artist_color = "#8D99AE"  # Cor padrão (alternative)
            
            for genre in artist['genres']:
                # Dividir géneros compostos (ex: "indie rock" -> ["indie", "rock"])
                genre_words = genre.lower().split()
                
                # Procurar cada palavra nos nossos géneros definidos
                for word in genre_words:
                    for genre_info in spotify_genres.values():
                        if word == genre_info["genre"]:
                            artist_color = genre_info["color"]
                            break
                    if artist_color != "#8D99AE":  # Se já encontrou uma cor, parar
                        break
                if artist_color != "#8D99AE":  # Se já encontrou uma cor, parar
                    break
            
            artist_info['color'] = artist_color
        else:
            # Se não tem géneros, usar cor padrão
            artist_info['color'] = "#8D99AE"
        artists_data.append(artist_info)
    
    return render_template('top-artists.html', artists=artists_data) #posso também alterar para thymeleaf
    #return jsonify(artists_data)

#@app.route('/top-tracks-from-top-artists')
def getTopTracksFromTopArtists():
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session['expires_at']:
        print("TOKEN EXPIRED,, REFRESHING..")
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    response = requests.get(API_BASE_URL + 'me/top/tracks?time_range=short_term', headers=headers)
    top_tracks = response.json()
    top_tracks_info = []
    for track in top_tracks['items']:
        info = {'name': track['name'],
        'artist': track['artists'][0]['name'] # artists é um array
        }
        top_tracks_info.append(info)

    #return jsonify(top_tracks_info)
    return top_tracks_info

'''
@app.route('/top-tracks')
def get_topTracks():
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session['expires_at']:
        print("TOKEN EXPIRED,, REFRESHING..")
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    response = requests.get(API_BASE_URL + 'me/top/artists?time_range=short_term', headers=headers)
    top_tracks = response.json()
    return jsonify(top_tracks)
'''

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("TOKEN EXPIRED,, REFRESHING..")
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in'] 

        return redirect('/top-artists')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug= True)