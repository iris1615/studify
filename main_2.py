import requests
import urllib.parse
import os

from flask import Flask, redirect, jsonify, session, request, render_template
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'random aah string'

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_SHARED_SECRET = os.getenv("LASTFM_SHARED_SECRET")
API_BASE_URL = 'http://ws.audioscrobbler.com/2.0/'
LASTFM_USERNAME = os.getenv("LASTFM_USERNAME")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_BASE_URL = 'https://api.spotify.com/v1/'

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
        
        return redirect('/top-artists')

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

'''
@app.route('/')
def index():
    return "Welcome to my app !! <a href='/top-artists'>View my top artists !!</a>"
'''
'''
The project is now Last.fm based, thus not requiring OAuth routes due to Last.fm's use of API key authentication instead of OAuth2:
    @app.route('/login') - Not needed for Last.fm
    @app.route('/callback') - Not needed for Last.fm
    @app.route('/refresh-token') - Not needed for Last.fm
'''
def get_spotify_artist_image(artist_name):
    """Get artist image from Spotify API"""
    if 'access_token' not in session:
        return None
    
    # Check if token is expired
    if datetime.now().timestamp() > session['expires_at']:
        # Try to refresh token
        try:
            refresh_token()
        except:
            return None
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    # Search for artist
    search_params = {
        'q': artist_name,
        'type': 'artist',
        'limit': 1
    }
    
    try:
        response = requests.get(
            SPOTIFY_BASE_URL + 'search', 
            headers=headers, 
            params=search_params
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['artists']['items']:
                artist = data['artists']['items'][0]
                if artist['images']:
                    # Get the largest available image
                    return artist['images'][0]['url']
        
        return None
        
    except Exception as e:
        print(f"Error getting Spotify image for {artist_name}: {e}")
        return None

def get_artist_image(artist):
    """Get artist image - try Spotify first, then Last.fm as fallback"""
    artist_name = artist['name']
    
    # Try Spotify first
    spotify_image = get_spotify_artist_image(artist_name)
    if spotify_image:
        return spotify_image
    

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

    spotify_authenticated = 'access_token' in session and datetime.now().timestamp() < session['expires_at']
    
    if not spotify_authenticated:
        # If not authenticated with Spotify, redirect to login
        return redirect('/login')

    params = {
        'method': 'user.getTopArtists',
        'user': os.getenv('LASTFM_USERNAME'),  # Or make it dynamic
        'api_key': LASTFM_API_KEY,
        'format': 'json',
        'period': '7day', 
        'limit': 20
    }

    try:
        response = requests.get(API_BASE_URL, params=params)
        data = response.json()
    except Exception as e:
        return f"Error fetching data from Last.fm: {e}", 500
    #artist_names = [artist['name'] for artist in top_artists['items']]
    #artist_images = [artist['images'] for artist in top_artists['items']]
    artists_data = []
    userTopTracksInfo = get_user_top_tracks()
    
    if 'topartists' in data and 'artist' in data['topartists']:
        for artist in data['topartists']['artist']:
            # Get additional artist info
            artist_info = get_artist_info(artist['name'])
            
            artist_data = {
                'name': artist['name'],
                'image_url': get_artist_image(artist),
                'playcount': artist['playcount'],
                'url': artist['url'],
                'tracks': [],  # You'll need to fetch top tracks separately
                'genres': artist_info.get('tags', []),
                'color': "#8D99AE"
            }
            if artist['name'] in userTopTracksInfo :
                user_tracks = userTopTracksInfo[artist['name']][:5]
                for track in user_tracks:
                    artist_data['tracks'].append(track['name'])
            # se necessário, adicionar 3 músicas populares do artista - não quero muito fazer isto pq queria que fosse completamente user based
            
            # Apply genre coloring logic (same as before)
            if artist_data['genres']:
                artist_data['color'] = get_genre_color(artist_data['genres'])
            
            artists_data.append(artist_data)
    
    return render_template('top-artists.html', artists=artists_data) #posso também alterar para thymeleaf
    #return jsonify(artists_data)

def get_artist_info(artist_name):
    """Get additional artist information including tags/genres"""
    params = {
        'method': 'artist.getInfo',
        'artist': artist_name,
        'api_key': LASTFM_API_KEY,
        'format': 'json'
    }
    
    response = requests.get(API_BASE_URL, params=params)
    data = response.json()
    
    if 'artist' in data:
        return {
            'tags': [tag['name'].lower() for tag in data['artist'].get('tags', {}).get('tag', [])],
            'bio': data['artist'].get('bio', {}).get('summary', ''),
            'listeners': data['artist'].get('stats', {}).get('listeners', 0)
        }
    return {}

'''
def get_artist_image(artist_name):
    """Extract artist image from Last.fm response"""
    images = artist.get('image', [])
    for img in images:
        if img['size'] == 'large' or img['size'] == 'extralarge':
            image_url = img['#text'] if img['#text'] else None
            #print(f"Selected image URL: {image_url}")  # Debug line
            return image_url
    return None
'''
def get_genre_color(genres):
    """Apply genre coloring logic (same as before)"""
    for genre in genres:
        genre_words = genre.lower().split()
        for word in genre_words:
            for genre_info in spotify_genres.values():
                if word == genre_info["genre"]:
                    return genre_info["color"]
    return "#8D99AE"

def get_top_tracks_for_artist(artist_name):
    """Get top tracks for a specific artist"""
    params = {
        'method': 'artist.getTopTracks',
        'artist': artist_name,
        'api_key': LASTFM_API_KEY,
        'format': 'json',
        'limit': 5
    }
    
    response = requests.get(API_BASE_URL, params=params)
    data = response.json()
    
    tracks = []
    if 'toptracks' in data and 'track' in data['toptracks']:
        tracks = [track['name'] for track in data['toptracks']['track']]
    
    return tracks

def get_user_top_tracks():
    params = {
        'method': 'user.getTopTracks',
        'limit': 50,
        'user': LASTFM_USERNAME,
        'api_key': LASTFM_API_KEY,
        'format': 'json',
        'period': '7day'
    }
    response = requests.get(API_BASE_URL, params=params)
    data = response.json()

    artist_tracks_dict = {}

    if 'toptracks' in data and 'track' in data['toptracks']:
        for track in data['toptracks']['track']:
            artist_name = track['artist']['name']
            track_name = track['name']
            playcount = int(track['playcount'])
            
            # If artist not in dict, create new entry
            if artist_name not in artist_tracks_dict:
                artist_tracks_dict[artist_name] = []
            
            # Add track info to artist's list
            track_info = {
                'name': track_name,
                'playcount': playcount,
                'url': track['url']
            }
            artist_tracks_dict[artist_name].append(track_info)
    
    # Sort tracks by playcount for each artist
    for artist in artist_tracks_dict:
        artist_tracks_dict[artist].sort(key=lambda x: x['playcount'], reverse=True)
    
    return artist_tracks_dict


#@app.route('/top-tracks-from-top-artists')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug= True)