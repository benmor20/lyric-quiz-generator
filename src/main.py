import json
import os

from spotify import Spotify
from lyrics import *


def main():
    playlist_id = '6MGdpQKVoZYFj9RZkcxcRw'
    spotify = Spotify()
    res = spotify.tracks_from_playlist(playlist_id)
    path = os.sep.join([os.path.relpath(__file__), '..', 'results.json'])
    with open(path, 'w') as results:
        results.write(json.dumps(res))


if __name__ == '__main__':
    main()
