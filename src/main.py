from spotify import Spotify
from lyrics import *


def main():
    title = '1985'
    artist = 'Bowling For Soup'
    full = get_full_lyrics(title, artist)
    no_chorus = remove_chorus(full)
    print()
    print(no_chorus)
    print()
    print(random_lyrics(title, artist))


if __name__ == '__main__':
    main()
