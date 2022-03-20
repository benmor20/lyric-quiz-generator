import bs4 as bs
import requests
import random
from typing import *


def get_full_lyrics(title: str, artist: str):
    # Create URL
    if ' (' in title:
        title = title.split(' (')[0]
    if ' -' in title:
        title = title.split(' -')[0]
    title = standardize_phrase(title)
    artist = standardize_phrase(artist)
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
    skip = False
    for line in lyrics.split('\n'):
        if len(line) == 0 or (line[0] == '(' and line[-1] == ')'):
            continue
        if line[0] == '[':
            skip = line[1:-1] == 'Chorus' or 'Album' in line
        elif not skip:
            no_chorus.append(line)
    return '\n'.join(no_chorus)


def random_lyrics(title: str, artist: str, max_attempts: int = 50):
    no_chorus = remove_chorus(get_full_lyrics(title, artist))
    if len(no_chorus) == 0:
        print(f'Could not find lyrics for {title} by {artist}')
        return None
    lines = no_chorus.split('\n')
    if len(lines) == 1:
        print(f'One line song for {title} by {artist}')
        return None
    lyrics = title.lower()
    attempt_num = 0
    while has_overlap(title, lyrics) or num_words(lyrics) <= 6:
        line_start = random.randrange(len(lines) - 1)
        lyrics = clean_phrase(lines[line_start])
        attempt_num += 1
        if attempt_num >= max_attempts:
            print(f'Could not find appropriate line for {title} by {artist}')
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


def standardize_phrase(phrase):
    replacements = {'\n': ' ',
                    '&': 'and',
                    '.': '',
                    ',': '',
                    '!': '',
                    '?': '',
                    '-': ' ',
                    ':': '',
                    '(': '',
                    ')': '',
                    '\'': '',
                    '"': '',
                    '/': ' ',
                    '+': ' ',
                    '#': ''}
    phrase = clean_phrase(phrase.lower())
    for target, replace in replacements.items():
        phrase = phrase.replace(target, replace)
    return phrase


def clean_phrase(phrase):
    replacements = {'\u2005': ' ',
                    '\u0435': 'e'}
    for target, replace in replacements.items():
        phrase = phrase.replace(target, replace)
    return phrase
