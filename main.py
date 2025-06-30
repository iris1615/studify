from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

load_dotenv() # vai dar load das variáveis de ambiente do arquivo .env

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
#print(f"Client ID: {client_id}")
#print(f"Client Secret: {client_secret}")

def get_token(): # o que precisamos sempre de meter no nosso header quando queremos fazer um request acerca de info do Spotify
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) > 0:
        return json_result[0]  # Return the first artist found
    else:
        return None
    #print(json_result)

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def get_my_top_tracks(token):
    url = f"https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=5"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

token = get_token()
print(get_my_top_tracks(token))
'''
response = search_for_artist(token, artist_name = "Ca7riel")
artist_id = response["id"]
songs = get_songs_by_artist(token, artist_id)
for song in songs:
    print(f"Song: {song['name']}, Popularity: {song['popularity']}")
'''