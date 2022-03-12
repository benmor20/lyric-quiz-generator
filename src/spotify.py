import os

import requests
import time


BASE_URL = 'https://api.spotify.com/v1'
SEARCH_URL = f'{BASE_URL}/search'


class Spotify:
    def __init__(self, client_id_path='client_id.txt', client_secret_path='client_secret.txt'):
        dir_path = os.sep.join([os.path.relpath(__file__), '..'])
        # Get the client and secret IDs from files stored and remove the newline
        with open(os.sep.join([dir_path, client_id_path]), 'r') as f:
            client_id = f.read().replace('\n', '')
        with open(os.sep.join([dir_path, client_secret_path]), 'r') as f:
            secret = f.read().replace('\n', '')

        # Authorize spotify, get access token
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_response = requests.post(auth_url, {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': secret,
        })
        auth_response_data = auth_response.json()
        access_token = auth_response_data['access_token']

        # Set headers
        self.headers = {
            'Authorization': f'Bearer {access_token}'
        }

    def query(self, q, type=None):
        # Set params
        params = {'q': q,
                  'limit': 1}
        if type is not None:
            params['type'] = type

        # Get response
        response = requests.get(SEARCH_URL, params=params, headers=self.headers)
        while response.status_code != 200:
            print("Failed Spotify Request")
            time.sleep(1)
            response = requests.get(SEARCH_URL, params=params, headers=self.headers)
        response = response.json()

        # Check that GET request doesn't return empty.
        if len(response["tracks"]["items"]) == 0:
            return None

        return response
