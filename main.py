from flask import flask, redirect
import requests
import urllib.parse

app = Flask(__name__)
app.secret_key = 'random aah string'

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

@app.route('/')
def index():
    return "Welcome to my spotify app !! <a href='/login'>Login with spotify</a>"

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True # forçar user a dar login - DEBUGGING,, podemos omitir
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)

