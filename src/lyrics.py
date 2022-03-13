import bs4 as bs
import requests
import random
from typing import *
from datetime import date

from spotify import Spotify


def get_full_lyrics(title: str, artist: str):
    # Create URL
    if ' (' in title:
        title = title.split(' (')[0]
    title = clean_phrase(title)
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
        if len(line) == 0:
            continue
        if line[0] == '[':
            in_chorus = 'Chorus' in line
        elif not in_chorus:
            no_chorus.append(line)
    return '\n'.join(no_chorus)


def random_lyrics(title: str, artist: str, max_attempts: int = 50):
    no_chorus = remove_chorus(get_full_lyrics(title, artist))
    if len(no_chorus) == 0:
        return None
    lines = no_chorus.split('\n')
    lyrics = title.lower()
    attempt_num = 0
    while has_overlap(title, lyrics) or num_words(lyrics) <= 5:
        line_start = random.randrange(len(lines) - 1)
        lyrics = lines[line_start].replace('\\u2005', ' ').replace('\u2005', ' ')
        attempt_num += 1
        if attempt_num >= max_attempts:
            return None
    return lyrics


def has_overlap(lyric1, lyric2):
    words1 = set(words_from_lyrics(lyric1))
    words2 = set(words_from_lyrics(lyric2))
    return len(words1 - words2) <= len(words1) * 0.75


def num_words(lyrics):
    return len(set(words_from_lyrics(lyrics)))


def words_from_lyrics(lyrics):
    return clean_phrase(lyrics).split(' ')


def clean_phrase(phrase):
    phrase = phrase.lower().replace('\n', ' ')
    phrase = phrase.replace('\u2005', ' ')
    phrase = phrase.replace('\\u2005', ' ')
    for c in '.,!?-:()':
        phrase = phrase.replace(c, '')
    return phrase
