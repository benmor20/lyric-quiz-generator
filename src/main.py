import json
import os

import requests

from spotify import Spotify
from lyrics import *
from song import *
from quiz import *


def to_rel_file(path):
    return os.sep.join([os.path.relpath(__file__), '..', path])


def main():
    playlist_id = '4CCu21yjMswqBGwMnEsjbu'
    answer_key = generate_quiz(100, playlist=playlist_id)
    print(answer_key)
    with open(to_rel_file('lyric_test.txt'), 'w', encoding='utf-8') as test_file:
        with open(to_rel_file('lyric_test_answers.txt'), 'w', encoding='utf-8') as answer_file:
            export_to_files(test_file, answer_file, answer_key)


if __name__ == '__main__':
    main()
