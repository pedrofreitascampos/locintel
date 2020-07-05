from itertools import islice


def is_a_in_x(A, X):
    if type(A) != type(X):
        A = list(A)
        X = list(X)

    for i in range(len(X) - len(A) + 1):
        if A == X[i : i + len(A)]:
            return True
    return False


def pairwise(iterable):
    """This function returns all contiguous pairs of elements in an iterator
    """
    return list(zip(iterable, iterable[1:]))


def tripletwise(iterable):
    return list(zip(iterable, iterable[1:], iterable[2:]))


def window(seq, n=3):
    """Returns a sliding window (of width n) over data from the iterable

    Args:
        seq (iterable): The iterable to slide on
        n (int): The width of tghe window

    Returns:
        generator: The generator of the windows

    """
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result
