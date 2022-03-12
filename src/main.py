import requests
import time
from spotify import Spotify


def main():
    spot = Spotify()
    etwt = spot.query('Everytime We Touch Cascada', type='track')
    print(etwt)


if __name__ == '__main__':
    main()
