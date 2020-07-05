from das.routing.core.datamodel.geo import GeoCoordinate
from das.routing.graphs.datamodel.jurbey import Mask
from das.routing.graphs.datamodel.osm import (
    Node as OsmNode,
    Way,
    Relation,
    ViaNode,
    ViaWays,
)
from unittest.mock import Mock

"""
        OSM Base Graph 

        1---2---3
                |
                4
                |
        7---6---5
        |
        8
            
"""

base_nodes = {
    1: OsmNode(
        id=1,
        coord=GeoCoordinate(lng=0, lat=0),
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    2: OsmNode(
        id=2,
        coord=GeoCoordinate(lng=1, lat=0),
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    3: OsmNode(
        id=3,
        coord=GeoCoordinate(lng=2, lat=0),
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    4: OsmNode(
        id=4,
        coord=GeoCoordinate(lng=2, lat=-1),
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    5: OsmNode(
        id=5,
        coord=GeoCoordinate(lng=2, lat=2),
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    6: OsmNode(
        id=6,
        coord=GeoCoordinate(lng=1, lat=-2),
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    7: OsmNode(
        id=7,
        coord=GeoCoordinate(lng=0, lat=-2),
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    8: OsmNode(
        id=8,
        coord=GeoCoordinate(lng=0, lat=-3),
        metadata={"version": 1, "hd_edges": "[]"},
    ),
}

base_ways = {
    1: Way(id=1, nodes=[1, 2, 3], tags={"version": 1, "highway": "primary"}),
    2: Way(id=2, nodes=[3, 4, 5], tags={"version": 1, "highway": "primary"}),
    3: Way(id=3, nodes=[7, 6, 5], tags={"version": 1, "highway": "primary"}),
    4: Way(id=4, nodes=[7, 8], tags={"version": 1, "highway": "primary"}),
}

base_relations = {
    (2, 3, 4): Relation(
        id=1,
        from_way=1,
        from_node=2,
        via=ViaNode(3),
        to_way=2,
        to_node=4,
        tags={"version": 1, "type": "restriction", "restriction": "no_right_turn"},
    ),
    (2, (3, 4, 5), 6): Relation(
        id=2,
        from_way=1,
        from_node=2,
        via=ViaWays((3, 4, 5), ways=[2]),
        to_way=3,
        to_node=6,
        tags={"version": 1, "type": "restriction", "restriction": "no_u_turn"},
    ),
    (6, 7, 8): Relation(
        id=3,
        from_way=3,
        from_node=6,
        via=ViaNode(7),
        to_way=4,
        to_node=8,
        tags={"version": 1, "type": "restriction", "restriction": "no_left_turn"},
    ),
}

base_data = Mock(nodes=base_nodes, ways=base_ways, relations=base_relations)

fake_mask = Mask(
    nodes={1, 2, 3, 4, 5, 6, 7},
    edges={(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)},
    relations={(1, 2, 3), (3, 4, 5), (4, 5, 6), (5, 6, 7)},
    hd_mapping={},
)

expected_nodes = {
    node_id: node
    for node_id, node in list(base_nodes.items())[:7]  # mask excludes last one
}

expected_ways = {
    1: Way(
        id=1,
        nodes=[1, 2, 3],
        tags={"version": 1, "highway": "primary", "oneway": "yes"},
    ),
    2: Way(
        id=2,
        nodes=[3, 4, 5],
        tags={"version": 1, "highway": "primary", "oneway": "yes"},
    ),
    3: Way(
        id=3,
        nodes=[5, 6, 7],
        tags={"version": 1, "highway": "primary", "oneway": "yes"},
    ),
}

expected_relations = {
    (2, 3, 4): Relation(
        1,
        from_way=1,
        from_node=2,
        via=ViaNode(3),
        to_way=2,
        to_node=4,
        tags=base_relations[(2, 3, 4)].tags,
    ),
    (2, (3, 4, 5), 6): Relation(
        2,
        from_way=1,
        from_node=2,
        via=ViaWays((3, 4, 5), ways=[2]),
        to_way=3,
        to_node=6,
        tags=base_relations[(2, (3, 4, 5), 6)].tags,
    ),
}


expected_data = Mock(
    nodes=expected_nodes, ways=expected_ways, relations=expected_relations
)
