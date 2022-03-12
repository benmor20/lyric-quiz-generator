import requests
import time


def setup_spotify():
    # Get the client and secret IDs from files stored and remove the newline
    with open('client_id.txt', 'r') as f:
        client_id = f.read().replace('\n', '')
    with open('client_secret.txt', 'r') as f:
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

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    return 'https://api.spotify.com/v1', headers


def get_request(base_url, params, headers):
    return requests.get(f'{base_url}/search', params=params, headers=headers)


def query_track(title, artist, base_url, headers):
    params = {'q': f'{title} {artist}',
              'type': 'track',
              'limit': 1}
    response = get_request(base_url, params, headers)
    while response.status_code != 200:
        print("Failed Spotify Request")
        time.sleep(1)
        response = get_request(base_url, params, headers)
    response = response.json()

    # Check that GET request doesn't return empty.
    if len(response["tracks"]["items"]) == 0:
        return None

    # Index the JSON file appropriately to find the Track ID
    # track_id = response["tracks"]["items"][0]["id"]

    return response


def main():
    base_url, headers = setup_spotify()
    etwt = query_track('Everytime We Touch', 'Cascada', base_url, headers)
    print(etwt)


if __name__ == '__main__':
    main()
