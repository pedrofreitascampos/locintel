from tests.synthetic.graphs import from_adjacency_list
from tests.synthetic.utils import simple_node_geometry

from unittest.mock import Mock

"""
========================================================

            Dummy HD Graph

                     16
       18 ← 17       ↑
            | \      ↑
        5 ← 4 ← 3 ←  2 ←  1  ← 0
          /        /           ↑
        6 → 7 → 8 → →  → 9  → 10
        ↓         \      /
        ↓          11   12
        15         ↓    ↑
                   13   14

========================================================

"""
nodes_data = {
    0: {"coords": [0, 0], "adjacency": [1]},
    1: {"coords": [-1, 0], "adjacency": [2]},
    2: {"coords": [-2, 0], "adjacency": [3, 16]},
    3: {"coords": [-3, 0], "adjacency": [4, 17]},
    4: {"coords": [-4, 0], "adjacency": [5, 6]},
    5: {"coords": [-5, 0], "adjacency": []},
    6: {"coords": [-5, -1], "adjacency": [15, 7]},
    7: {"coords": [-4, -1], "adjacency": [8]},
    8: {"coords": [-3, -1], "adjacency": [2, 9, 11]},
    9: {"coords": [-1, -1], "adjacency": [10]},
    10: {"coords": [0, -1], "adjacency": [0]},
    11: {"coords": [-2.5, -2], "adjacency": [13]},
    12: {"coords": [-1.5, -2], "adjacency": [9]},
    13: {"coords": [-2.5, -3], "adjacency": []},
    14: {"coords": [-1.5, -3], "adjacency": [12]},
    15: {"coords": [-5, -2], "adjacency": []},
    16: {"coords": [-2, 2], "adjacency": []},
    17: {"coords": [-4, 1.5], "adjacency": [18]},
    18: {"coords": [-5, 1.5], "adjacency": []},
}

edges_data = {
    1: {"nodes": (0, 1), "metadata": {}},
    2: {"nodes": (1, 2), "metadata": {}},
    3: {"nodes": (2, 3), "metadata": {}},
    4: {"nodes": (2, 16), "metadata": {}},
    5: {"nodes": (3, 4), "metadata": {}},
    6: {"nodes": (4, 5), "metadata": {}},
    7: {"nodes": (4, 6), "metadata": {}},
    8: {"nodes": (6, 15), "metadata": {}},
    9: {"nodes": (6, 7), "metadata": {}},
    10: {"nodes": (7, 8), "metadata": {}},
    11: {"nodes": (8, 9), "metadata": {}},
    12: {"nodes": (8, 2), "metadata": {}},
    13: {"nodes": (9, 10), "metadata": {}},
    14: {"nodes": (10, 0), "metadata": {}},
    15: {"nodes": (8, 11), "metadata": {}},
    16: {"nodes": (11, 13), "metadata": {}},
    17: {"nodes": (14, 12), "metadata": {}},
    18: {"nodes": (12, 9), "metadata": {}},
    19: {"nodes": (3, 17), "metadata": {}},
    20: {"nodes": (17, 18), "metadata": {}},
    21: {"nodes": (4, 17), "metadata": {"virtual_lane": True}},
    22: {"nodes": (17, 4), "metadata": {"virtual_lane": True}},
}

adjacency_list = {
    node_id: [
        edge["nodes"][1]
        for edge in edges_data.values()
        if edge["nodes"][0] == node_id and "virtual_lane" not in edge["metadata"]
    ]
    for node_id in nodes_data
}

adjacency_list_with_virtual_lanes = {
    node_id: [
        edge["nodes"][1] for edge in edges_data.values() if edge["nodes"][0] == node_id
    ]
    for node_id in nodes_data
}
coordinates = {
    node_id: Mock(lat=data["coords"][0], lng=data["coords"][1])
    for node_id, data in nodes_data.items()
}


graph = from_adjacency_list(
    "test_graph",
    adjacency_list,
    coordinates,
    simple_node_geometry,
    metadata_func=lambda x: (x[0], x[1]),
)
graph_with_virtual_lanes = from_adjacency_list(
    "test_graph",
    adjacency_list_with_virtual_lanes,
    coordinates,
    simple_node_geometry,
    metadata_func=lambda x: (x[0], x[1]),
)
