import json
import os

from spotify import Spotify
from lyrics import *
from quiz import *


def to_rel_file(path):
    return os.sep.join([os.path.relpath(__file__), '..', path])


def main():
    playlist_id = ''
    answer_key = generate_quiz(20, album='Hamilton (Original Broadway Cast Recording)', limit=60)
    print(answer_key)
    with open(to_rel_file('lyric_test.txt'), 'w', encoding='utf-8') as test_file:
        with open(to_rel_file('lyric_test_answers.txt'), 'w', encoding='utf-8') as answer_file:
            export_to_files(test_file, answer_file, answer_key)


if __name__ == '__main__':
    main()
