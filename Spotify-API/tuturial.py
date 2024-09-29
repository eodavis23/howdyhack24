import requests
import urllib.parse

from datetime import datetime, timedelta
from flask import Flask, redirect, request, jsonify, session

app = Flask(__name__)
app.secret_key = "53d355f8-571a-490-a310-1f9579440851"

CLIENT_ID = 'd8d8018ff79545c3a7871ee450361b97'
CLIENT_SECRET = '07b5045b76084a56ab4a61359c802c27'
REDIRECT_URL = 'http://localhost:5000/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1'


@app.route('/')
def index():
    #Flask load example
    return "Welcome to my Spotify App <a href='login'>Login with Spotify</a>"

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URL,
        'show_dialog': False #Delete after you know its working
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    print('hello world')

    return redirect(auth_url)

@app.route('/callback')
def callback():
    print('Hello We hit callback')
    if 'error' in request.args:
        print('We got an error. Oh no')
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        print('It apparently works.')
        print(request.args)
        req_body = {
            'code': request.args['code'],
            'grant_type': "authorization_code",
            'redirect_uri': REDIRECT_URL,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()
        print(token_info)
        
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
        return redirect('/playlists')
    
@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('./refresh_token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    playlists = response.json()

    return jsonify(playlists)

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'authorization_code',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('/playlists')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)