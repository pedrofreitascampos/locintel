from itertools import chain, product

from das.routing.core.datamodel.geo import GeoCoordinate
from das.routing.graphs.datamodel.jurbey import Jurbey, Node

from tests.synthetic.utils import (
    create_edge,
    no_geometry,
    simple_node_geometry,
    interpolated_geometry,
)

########################################################
#              Hand-crafted Base Graphs                #
#                                                      #
#  These leverage knowledge of challenging             #
#  real-world situations when routing                  #
#                                                      #
########################################################
"""
Title: Simple urban grid network
 1      2       3        4       5       6
 +------+-------+--------+-------+-------+
 ^      |       |        |       ^       |
 |      |       |        |       |       |
 |      |       |        |       |       |
7+---------------------------------------+8
 |      |       |        |       |       |
 |      |       |        |       |       |
 |      |       |        |       |       |
 +------+-------+<-------+-------+-------+
 9     10      11       12      13      14
Tags: grid, oneway, overpass, bridge
"""
urban_grid_adjacency_list = {
    1: [2],
    2: [1, 3, 10],
    3: [2, 4, 11],
    4: [3, 5, 12],
    5: [4, 6],
    6: [5, 8],
    7: [1, 8, 9],
    8: [6, 7, 14],
    9: [7, 10],
    10: [2, 9, 11],
    11: [3, 10],
    12: [4, 11, 13],
    13: [5, 12, 14],
    14: [8, 13],
}
node_coordinates = {
    1: GeoCoordinate(0, 0),
    2: GeoCoordinate(0.001, 0),
    3: GeoCoordinate(0.0022, 0),
    4: GeoCoordinate(0.0029, 0),
    5: GeoCoordinate(0.0045, 0),
    6: GeoCoordinate(0.0053, 0),
    7: GeoCoordinate(0, -0.001),
    8: GeoCoordinate(0.0054, -0.0011),
    9: GeoCoordinate(0, -0.002),
    10: GeoCoordinate(0.001, -0.002),
    11: GeoCoordinate(0.0022, -0.002),
    12: GeoCoordinate(0.0029, -0.002),
    13: GeoCoordinate(0.0045, -0.002),
    14: GeoCoordinate(0.0053, -0.002),
}


def from_adjacency_list(name, adj_list, coordinates, geometry_policy, **kwargs):
    graph = Jurbey(metadata={"version": name})
    graph.add_nodes_from(
        [(i, {"data": Node(coord=coordinates[i])}) for i in adj_list.keys()]
    )
    edges = chain(*[(product([node], to_nodes)) for node, to_nodes in adj_list.items()])
    edges = [
        (
            edge[0],
            edge[1],
            {
                "data": create_edge(
                    geometry=geometry_policy(
                        graph.nodes[edge[0]]["data"].coord,
                        graph.nodes[edge[1]]["data"].coord,
                    ),
                    **dict(metadata=dict(hd_lane_id=kwargs["metadata_func"](edge)))
                    if "metadata_func" in kwargs
                    else {}
                )
            },
        )
        for edge in edges
    ]
    graph.add_edges_from(edges)
    return graph


urban_grid_no_geometry = from_adjacency_list(
    "urban_grid_no_geometry",
    urban_grid_adjacency_list,
    node_coordinates,
    geometry_policy=no_geometry,
)
urban_grid_node_geometry = from_adjacency_list(
    "urban_grid_node_geometry",
    urban_grid_adjacency_list,
    node_coordinates,
    geometry_policy=simple_node_geometry,
)
urban_grid_node_and_edge_geometry = from_adjacency_list(
    "urban_grid_node_and_edge_geometry",
    urban_grid_adjacency_list,
    node_coordinates,
    geometry_policy=interpolated_geometry,
)
