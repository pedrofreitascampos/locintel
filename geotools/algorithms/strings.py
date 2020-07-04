import string


def levenshtein_distance(s, t, alphabet=string.printable, **weight_dict):
    """
    Calculates Levenshtein distance between strings (iterative version)

    See https://en.wikipedia.org/wiki/Levenshtein_distance for more details

    :param s: string s
    :param t: string t
    :param alphabet: characters to consider
    :param weight_dict: keyword parameters setting the costs for characters, the default value for a character will be 1
    """
    if len(s) == 0 or len(t) == 0:
        return max([len(s), len(t)])

    rows = len(s) + 1
    cols = len(t) + 1

    w = dict((x, (1, 1, 1)) for x in alphabet + alphabet.upper())
    if weight_dict:
        w.update(weight_dict)

    dist = [[0 for _ in range(cols)] for _ in range(rows)]
    # source prefixes can be transformed into empty strings
    # by deletions:
    for row in range(1, rows):
        dist[row][0] = dist[row - 1][0] + w[s[row - 1]][0]
    # target prefixes can be created from an empty source string
    # by inserting the characters
    for col in range(1, cols):
        dist[0][col] = dist[0][col - 1] + w[t[col - 1]][1]

    for col in range(1, cols):
        for row in range(1, rows):
            deletes = w[s[row - 1]][0]
            inserts = w[t[col - 1]][1]
            subs = max((w[s[row - 1]][2], w[t[col - 1]][2]))
            if s[row - 1] == t[col - 1]:
                subs = 0
            else:
                subs = subs
            dist[row][col] = min(
                dist[row - 1][col] + deletes,
                dist[row][col - 1] + inserts,
                dist[row - 1][col - 1] + subs,
            )  # substitution

    return dist[row][col]
