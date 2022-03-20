import json

from lyrics import *
from spotify import Spotify


def generate_quiz(nsongs: int, spotify: Optional[Spotify] = None, min_popularity: int = 0, **kwargs):
    if spotify is None:
        spotify = Spotify()

    if 'playlist' in kwargs:
        response = spotify.tracks_from_playlist(kwargs['playlist'])
    else:
        response = spotify.query(**kwargs)
    if response is None:
        print('No songs found')
        return
    print(json.dumps(response))
    print(f'Got {len(response)} tracks')
    random.shuffle(response)
    if min_popularity > 0:
        response = [r for r in response if 'popularity' in r and r['popularity'] > min_popularity]
        print(f'Popularity filtered down to {len(response)} tracks')

    answer_key = {}
    for i, song in enumerate(response):
        # Pull song info
        title = song['name']
        artists = [a['name'] for a in song['artists']]
        artist = ', '.join(artists)

        # Create lyrics
        lyrics = random_lyrics(title, artists[0])
        if lyrics is not None:
            answer_key[lyrics] = (title, artist)
            print(f'{len(answer_key)}/{nsongs}')

        # break if done
        if len(answer_key) >= nsongs:
            break
    return answer_key


def export_to_files(test_file, answer_file, answer_key):
    headers = 'Lyric|Song|Artist\n'
    test_file.write(headers)
    answer_file.write(headers)
    test_file.writelines((f'{lyric}||\n' for lyric in answer_key))
    answer_file.writelines((f'{l}|{t}|{a}\n' for l, (t, a) in answer_key.items()))
