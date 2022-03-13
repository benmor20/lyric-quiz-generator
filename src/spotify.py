import json
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

        # Set headers
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    @staticmethod
    def _get_response(response_func):
        response = response_func()
        while 'error' in response:
            print(f"Failed Spotify Request: {response['error']['status']}, {response['error']['message']}")
            if response['error']['status'] == 404:
                return None
            time.sleep(1)
            response = response_func()
        return response

    def _response_from_query(self, url, params):
        res = requests.get(url, params=params, headers=self.headers)
        res = res.json()
        if "error" in res:
            return res
        print(json.dumps(res))
        return res['tracks']

    def query(self, name: Optional[str] = None, type: str = 'track', limit: int = 500, **kwargs):
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
        print(params)
        assert len(params) > 0

        # Get response
        response = self._get_response(lambda: self._response_from_query(SEARCH_URL, params))

        # Check that GET request doesn't return empty.
        if response is None or len(response['items']) == 0:
            return None

        return self._add_next(response['items'], response, max_amount=limit)

    def _response_from_url(self, url):
        res = requests.get(url, headers=self.headers)
        res = res.json()
        if "error" in res:
            return res
        print(json.dumps(res))
        while True:
            if isinstance(res, list):
                if len(res) == 0:
                    return []
                if isinstance(res[0], dict) and 'track' in res[0]:
                    return [r['track'] for r in res]
                return res
            elif 'items' in res:
                res = res['items']
            elif 'tracks' in res:
                res = res['tracks']
            else:
                raise ValueError('Uh no fucken clue dude')

    def query_from_url(self, url, limit: int = 500):
        response = self._get_response(lambda: self._response_from_url(url))

        # Check that GET request doesn't return empty.
        if response is None or len(response) == 0:
            return None

        return self._add_next(response, response, max_amount=limit)

    def tracks_from_playlist(self, playlist_id):
        response = self._get_response(lambda: requests.get(f'{PLAYLIST_URL}/{playlist_id}/tracks', headers=self.headers).json())
        tracks = [r['track'] for r in response['items']]

        # Check that GET request doesn't return empty.
        if len(tracks) == 0:
            return None

        return self._add_next(tracks, response)

    def _add_next(self, results, response, max_amount=500):
        if len(results) >= max_amount:
            return results
        if 'next' in response and response['next']:
            nxt = self.query_from_url(response['next'], limit=max_amount-len(results))
            if nxt:
                try:
                    results.extend(nxt)
                except KeyError as e:
                    print(json.dumps(results))
                    raise e
        return results
