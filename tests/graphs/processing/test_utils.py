from das.routing.graphs.processing.utils import (
    get_nodes_list,
    find_common_node,
    get_adjacent_node,
    sort_nodes,
)


def test_get_nodes_list():
    res = [[1, 2, 3, 4, 5]]
    loop = [(4, 8), (8, 7), (6, 2), (9, 5), (2, 5), (7, 6)]
    assert get_nodes_list([[1, 2], [2, 3], [3, 4], [4, 5]]) == res
    assert get_nodes_list([[2, 3], [1, 2], [3, 4], [4, 5]]) == res
    assert get_nodes_list([[4, 5], [3, 4], [2, 3], [1, 2]]) == res
    assert get_nodes_list([[1, 2], [4, 5], [3, 4], [2, 3]]) == res
    assert get_nodes_list(loop) == [[9, 5], [4, 8, 7, 6, 2, 5]]


def test_find_common_node():

    nodes_1 = [1, 2, 3, 4]
    nodes_2 = [4, 5, 6, 7]

    expected_result = 4

    actual_result = find_common_node(nodes_1, nodes_2)

    assert actual_result == expected_result

    # ===============================================

    nodes_1 = (1, 2, 3, 4)
    nodes_2 = (4, 5, 6, 7)

    expected_result = 4

    actual_result = find_common_node(nodes_1, nodes_2)

    assert actual_result == expected_result

    # ===============================================

    nodes_1 = (1, 2, 3, 4)
    nodes_2 = (5, 6, 7, 8)

    actual_result = find_common_node(nodes_1, nodes_2)

    assert not actual_result


def test_get_adjacent_node():

    nodes = [1, 2, 3, 4]
    via_node = 1

    expected_result = 2

    actual_result = get_adjacent_node(nodes, via_node)

    assert actual_result == expected_result

    # ===============================================

    nodes = [1, 2, 3, 4]
    via_node = 4

    expected_result = 3

    actual_result = get_adjacent_node(nodes, via_node)

    assert actual_result == expected_result

    # ===============================================

    nodes = [1, 2, 3, 4]
    via_node = 2

    expected_result = None

    actual_result = get_adjacent_node(nodes, via_node)

    assert actual_result == expected_result

    # ===============================================

    nodes = [1, 2, 3, 4]
    via_node = 5

    expected_result = None

    actual_result = get_adjacent_node(nodes, via_node)

    assert actual_result == expected_result


def test_sort_nodes():

    current_nodes = [1, 2, 3]
    new_nodes = [3, 4]

    expected_result = (1, 2, 3, 4)

    actual_result = sort_nodes(current_nodes, new_nodes)

    assert actual_result == expected_result

    # ===============================================

    current_nodes = [1, 2, 3]
    new_nodes = [5, 4]

    expected_result = (1, 2, 3, 5, 4)

    actual_result = sort_nodes(current_nodes, new_nodes)

    assert actual_result == expected_result
