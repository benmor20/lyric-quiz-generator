import os
from typing import *

import requests
import time


BASE_URL = 'https://api.spotify.com/v1'
SEARCH_URL = f'{BASE_URL}/search'
PLAYLIST_URL = f'{BASE_URL}/playlists'


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
        print(access_token)

        # Set headers
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    @staticmethod
    def _get_response(response_func):
        response = response_func()
        while 'status_code' in response and response['status_code'] != 200:
            print(f"Failed Spotify Request: {response.status_code}")
            time.sleep(1)
            response = response_func()
        return response

    def query(self, name: Optional[str] = None, type: str = 'track', limit: int = 1000, **kwargs):
        # Set params
        params = {}
        if name:
            params['q'] = name
        rem_params = ' '.join(f'{k}:{v}' for k, v in kwargs.items())
        if 'q' in params:
            params['q'] += f' {rem_params}'
        else:
            params['q'] = rem_params

        if type is not None:
            params['type'] = type
        if limit:
            params['limit'] = limit
        print(params)
        assert len(params) > 0

        # Get response
        response = self._get_response(lambda: requests.get(SEARCH_URL, params=params, headers=self.headers).json()['tracks'])

        # Check that GET request doesn't return empty.
        if len(response['items']) == 0:
            return None

        return self._add_next(response['items'], response)

    def query_from_url(self, url):
        response = self._get_response(lambda: requests.get(url, headers=self.headers).json()['tracks'])

        # Check that GET request doesn't return empty.
        if len(response['items']) == 0:
            return None

        return self._add_next(response['items'], response)

    def tracks_from_playlist(self, playlist_id):
        response = self._get_response(lambda: requests.get(f'{PLAYLIST_URL}/{playlist_id}/tracks', headers=self.headers).json())

        # Check that GET request doesn't return empty.
        if len(response['items']) == 0:
            return None

        return self._add_next(response['items'], response)

    def _add_next(self, results, response):
        if 'next' in response and response['next']:
            nxt = self.query_from_url(response['next'])
            if nxt:
                results.extend(nxt)
        return results
