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


def split_lyrics(lyrics):
    lines = lyrics.split('\n')
    res = []
    cur_section = None
    cur_lyrics = []
    for line in lines:
        if line[0] == '[':
            if len(cur_lyrics) > 0:
                res.append((cur_section, cur_lyrics))
            cur_section = line[1:-1].lower()
            cur_lyrics = []
            continue
        cur_lyrics.append(line)
    if len(cur_lyrics) > 0:
        res.append((cur_section, cur_lyrics))
    return res


def remove_chorus(lyrics):
    if lyrics is None or len(lyrics) == 0:
        return None
    splt = split_lyrics(lyrics)
    return [l for s, l in splt if s is None or (s != 'chorus' and 'album' not in s)]


def random_lyrics(song, max_attempts: int = 50):
    title = song['name']
    artists = ', '.join(a['name'] for a in song['artists'])
    no_chorus = remove_chorus(get_full_lyrics(song))
    if no_chorus is None or len(no_chorus) == 0:
        print(f'Could not find lyrics for {title} by {artists}')
        return None
    lyrics = title.lower()
    attempt_num = 0
    while has_overlap(title, lyrics) or num_words(lyrics) <= 6:
        lines = random.choice(no_chorus)
        line_start = random.randrange(len(lines))
        lyrics = clean_phrase(lines[line_start])
        if num_words(lyrics) <= 6 and line_start < len(lines) - 1:
            nxt = clean_phrase(lines[line_start + 1])
            lyrics += ' / ' + nxt

        attempt_num += 1
        if attempt_num > max_attempts:
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
