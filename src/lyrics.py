import bs4 as bs
import requests
import random
from typing import *

from song import *


def get_full_lyrics(song):
    if song is None:
        return
    for title, artist in title_and_artist_pairs_from_song(song):
        # Create URL
        title_dashed = '-'.join(title.lower().split(' '))
        artist_dashed = '-'.join(artist.lower().split(' '))
        lyric_subdomain = '-'.join([artist_dashed, title_dashed, 'lyrics'])
        url = f'https://genius.com/{lyric_subdomain}'

        # Get soup
        page = requests.get(url)
        if page.status_code != 200:
            continue
        soup = bs.BeautifulSoup(page.text, 'html.parser')

        lyrics = lyrics_from_soup(soup)
        if len(lyrics) > 0:
            # print(f'Song is {title}, artist is {artist}')
            return lyrics


def lyrics_from_soup(soup):
    all_lyrics = soup.find_all("div", **{"data-lyrics-container": "true"})
    lyrics = '\n'.join(l.get_text('\n') for l in all_lyrics)
    return lyrics


def remove_chorus(lyrics):
    if lyrics is None or len(lyrics) == 0:
        return None
    no_chorus = []
    skip = False
    for line in lyrics.split('\n'):
        if len(line) == 0 or (line[0] == '(' and line[-1] == ')'):
            continue
        if line[0] == '[':
            skip = line[1:-1] == 'Chorus' or 'Album' in line
        elif not skip:
            no_chorus.append(line)
    return '\n'.join(no_chorus)


def random_lyrics(song, max_attempts: int = 50):
    title = song['name']
    artists = ', '.join(a['name'] for a in song['artists'])
    no_chorus = remove_chorus(get_full_lyrics(song))
    if no_chorus is None or len(no_chorus) == 0:
        print(f'Could not find lyrics for {title} by {artists}')
        return None
    lines = no_chorus.split('\n')
    if len(lines) == 1:
        print(f'One line song for {title} by {artists}')
        return None
    lyrics = title.lower()
    attempt_num = 0
    while has_overlap(title, lyrics) or num_words(lyrics) <= 6:
        line_start = random.randrange(len(lines) - 1)
        lyrics = clean_phrase(lines[line_start])
        attempt_num += 1
        if attempt_num >= max_attempts:
            print(f'Could not find appropriate line for {title} by {artists}')
            return None
    return lyrics


def has_overlap(lyric1, lyric2):
    words1 = set(words_from_lyrics(lyric1))
    words2 = set(words_from_lyrics(lyric2))
    return len(words1 - words2) <= len(words1) * 0.75


def num_words(lyrics):
    return len(set(words_from_lyrics(lyrics)))


def words_from_lyrics(lyrics):
    return standardize_phrase(lyrics).split(' ')
