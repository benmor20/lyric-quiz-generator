import itertools


def possible_titles(title):
    titles = [title]
    if ' (' in title:
        start, end = title.find(' (') + 1, title.find(') ')
        titles.append(title[:start - 1])
        parens = title[start + 1:end].lower()
        if not ('ft.' in parens or 'feat.' in parens or 'featuring' in parens):
            titles.append(parens)
    if ' - ' in title:
        # Assuming there's only one dash
        titles.extend([t for t in title.split(' - ') if 'remastered' not in t.lower()])
    return [clean_phrase(t) for t in titles]


def possible_artists(artists):
    poss_names = list(set(a for a in _possible_artists(artists) if len(a) > 0))
    names_split = [n.split(', ') for n in poss_names]
    longest = len(max(names_split, key=len))
    def key(a):
        l = len(a.split(', '))
        return 1.5 if l == longest else l
    return sorted(poss_names, key=key)


def _possible_artists(artists):
    if len(artists) == 1:
        yield artists[0]
        return
    for i, a in enumerate(artists):
        nxt_artists = list(_possible_artists(artists[:i] + artists[i+1:]))
        yield from nxt_artists
        yield from (f'{a}, {n}' for n in nxt_artists)


def title_and_artist_pairs_from_song(song):
    # Get all clean titles
    title = song['name']
    titles = possible_titles(title)
    clean_titles = []
    for t in titles:
        clean_titles.extend(possible_phrases(t))

    # Get all clean artists
    artist_names = [a['name'] for a in song['artists']]
    artists = possible_artists(artist_names)
    clean_artists = []
    for a in artists:
        clean_artists.extend(possible_phrases(a))

    # yield every combo
    yield from itertools.product(clean_titles, clean_artists)


def standardize_phrase(phrase):
    return possible_phrases(phrase)[0]


REPLACEMENTS = {
    '\n': [' '],
    '&': ['and', ' and ', ' '],
    '.': [''],
    ',': [''],
    '!': [''],
    '?': [''],
    '-': [' ', ''],
    ':': [''],
    '(': [''],
    ')': [''],
    '\'': [''],
    '"': [''],
    '´': [''],
    '/': [' '],
    '+': [' '],
    '#': [''],
    'à': ['a', '', 'à'],
    'á': ['a', '', 'á'],
    'â': ['a', '', 'â'],
    'ã': ['a', '', 'ã'],
    'ä': ['a', '', 'ä'],
    'å': ['a', '', 'å'],
    'æ': ['a', '', 'ae', 'æ'],
    'ç': ['c', '', 'ç'],
    'è': ['e', '', 'è'],
    'é': ['e', '', 'é'],
    'ê': ['e', '', 'ê'],
    'ë': ['e', '', 'ë'],
    'ì': ['i', '', 'ì'],
    'í': ['i', '', 'í'],
    'î': ['i', '', 'î'],
    'ï': ['i', '', 'ï'],
    'ñ': ['n', '', 'ñ'],
    'ò': ['o', '', 'ò'],
    'ó': ['o', '', 'ó'],
    'ô': ['o', '', 'ô'],
    'õ': ['o', '', 'õ'],
    'ö': ['o', '', 'ö'],
    'ø': ['o', '', 'ø'],
    'ù': ['u', '', 'ù'],
    'ú': ['u', '', 'ú'],
    'û': ['u', '', 'û'],
    'ü': ['u', '', 'ü'],
    'ý': ['y', '', 'ý'],
    'ÿ': ['y', '', 'ÿ'],
}


def possible_phrases(phrase):
    return [clean_phrase(a) for a in _possible_phrases(phrase.lower(), REPLACEMENTS)]


def _possible_phrases(phrase, replacements):
    target, replace = next(iter(replacements.items()))

    if target in phrase:
        if len(replacements) == 1:
            yield from (phrase.replace(target, r) for r in replace)
        else:
            new_replacements = {k: v for k, v in replacements.items() if k != target}
            for r in replace:
                yield from _possible_phrases(phrase.replace(target, r), new_replacements)
    else:
        if len(replacements) == 1:
            yield phrase
        else:
            new_replacements = {k: v for k, v in replacements.items() if k != target}
            yield from _possible_phrases(phrase, new_replacements)


# These are unexpected and I think just typos on the part of genius.com
CLEAN_REPLACEMENTS = {'\u2005': ' ',
                      '\u0435': 'e'}


def clean_phrase(phrase):
    while '  ' in phrase:
        phrase = phrase.replace('  ', ' ')
    for target, replace in CLEAN_REPLACEMENTS.items():
        phrase = phrase.replace(target, replace)
    return phrase
