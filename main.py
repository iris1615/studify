from flask import flask
import requests

app = Flask(__name__)
app.secret_key = 'random aah string'

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'