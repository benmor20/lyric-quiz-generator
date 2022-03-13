import bs4 as bs
import requests
import random
from typing import *
from datetime import date

from spotify import Spotify


def get_full_lyrics(title: str, artist: str):
    # Create URL
    title_dashed = '-'.join(title.lower().split(' '))
    artist_dashed = '-'.join(artist.lower().split(' '))
    lyric_subdomain = '-'.join([artist_dashed, title_dashed, 'lyrics'])
    url = f'https://genius.com/{lyric_subdomain}'

    # Get soup
    # print(f'url is {url}')
    page = requests.get(url)
    soup = bs.BeautifulSoup(page.text, 'html.parser')
    # print(soup.prettify())

    return lyrics_from_soup(soup)


def lyrics_from_soup(soup):
    all_lyrics = soup.find_all("div", **{"data-lyrics-container": "true"})
    lyrics = '\n'.join(l.get_text('\n') for l in all_lyrics)
    return lyrics


def remove_chorus(lyrics):
    no_chorus = []
    in_chorus = False
    for line in lyrics.split('\n'):
        if line[0] == '[':
            in_chorus = 'Chorus' in line
        elif not in_chorus:
            no_chorus.append(line)
    return '\n'.join(no_chorus)


def random_lyrics(title: str, artist: str):
    no_chorus = remove_chorus(get_full_lyrics(title, artist))
    lines = no_chorus.split('\n')
    lyrics = title.lower()
    while has_overlap(title, lyrics) or num_words(lyrics) <= 5:
        line_start = random.randrange(len(lines) - 1)
        lyrics = lines[line_start]
    return lyrics


def has_overlap(lyric1, lyric2):
    words1 = set(words_from_lyrics(lyric1))
    words2 = set(words_from_lyrics(lyric2))
    return len(words1 - words2) <= len(words1) * 0.75


def num_words(lyrics):
    return len(set(words_from_lyrics(lyrics)))


def words_from_lyrics(lyrics):
    lyrics = lyrics.lower().replace('\n', ' ')
    for c in '.,!?-:()':
        lyrics = lyrics.replace(c, '')
    return lyrics.split(' ')
