from das.routing.core.algorithms.itertools import (
    window,
    pairwise,
    tripletwise,
    is_a_in_x,
)

import pytest


def test_is_a_in_x():

    larger_list = [1, 2, 3, 4, 5, 6, 7]

    # ===============================================

    smaller_list = [3, 4, 5]

    expected_result = True

    actual_result = is_a_in_x(smaller_list, larger_list)

    assert actual_result == expected_result

    # ===============================================

    smaller_list = [2, 4, 5]

    expected_result = False

    actual_result = is_a_in_x(smaller_list, larger_list)

    assert actual_result == expected_result

    # ===============================================

    smaller_list = (3, 4, 5)

    expected_result = True

    actual_result = is_a_in_x(smaller_list, larger_list)

    assert actual_result == expected_result


def test_pairwise():

    iterable_1 = [1, 2, 3, 4]
    iterable_2 = (1, 2, 3, 4)
    iterable_3 = (1,)

    expected_pairs_1 = [(1, 2), (2, 3), (3, 4)]
    expected_pairs_2 = [(1, 2), (2, 3), (3, 4)]
    expected_pairs_3 = []

    pairs_1 = pairwise(iterable_1)
    pairs_2 = pairwise(iterable_2)
    pairs_3 = pairwise(iterable_3)

    assert pairs_1 == expected_pairs_1
    assert pairs_2 == expected_pairs_2
    assert pairs_3 == expected_pairs_3


def test_tripletwise():

    iterable_1 = [1, 2, 3, 4, 5]
    iterable_2 = (1, 2, 3, 4, 5)
    iterable_3 = (1, 2)

    expected_triplets_1 = [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
    expected_triplets_2 = [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
    expected_triplets_3 = []

    triplets_1 = tripletwise(iterable_1)
    triplets_2 = tripletwise(iterable_2)
    triplets_3 = tripletwise(iterable_3)

    assert triplets_1 == expected_triplets_1
    assert triplets_2 == expected_triplets_2
    assert triplets_3 == expected_triplets_3


def test_window():
    assert list(window(range(3), n=2)) == [(0, 1), (1, 2)]
    assert list(window(range(3), n=3)) == [(0, 1, 2)]
    assert list(window(range(1), n=3)) == []
