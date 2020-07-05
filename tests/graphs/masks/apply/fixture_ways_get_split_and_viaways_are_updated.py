from locintel.core.datamodel.geo import GeoCoordinate
from locintel.graphs.datamodel.jurbey import Mask
from locintel.graphs.datamodel.osm import (
    Node as OsmNode,
    Way,
    Relation,
    ViaWays,
    ViaNode,
)

from unittest.mock import Mock

"""
============================================================

    Test Case 2 - 
    - Mock get split when via nodes are not
      at start or end.
    - Mock with Mock are updated when referring its via way changes. 

                        6
                        |
                    1---2---3
                    |       |
                    4       5

nodes:        (1, 2, 3, 4, 5, 6)

ways:         1: (1, 2, 3, {"oneway": true})
              2: (4, 1, {"oneway": true})
              3: (3, 5, {"oneway": true})
              4: (2, 6, {})

restrictions: 1: (w2@from, n4@from, w1@via, w3@to, n5@to)
              2: (w4@from, n6@from, n2@via, w1@to, n3@to)

============================================================              
"""

base_nodes = {
    1: OsmNode(
        id=1,
        coord=GeoCoordinate(lng=-1.0, lat=0.0),
        ways=[1, 2],
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    2: OsmNode(
        id=2,
        coord=GeoCoordinate(lng=0.0, lat=0.0),
        ways=[2, 4],
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    3: OsmNode(
        id=3,
        coord=GeoCoordinate(lng=1.0, lat=0.0),
        ways=[1, 3],
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    4: OsmNode(
        id=4,
        coord=GeoCoordinate(lng=-1.0, lat=-1.0),
        ways=[2],
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    5: OsmNode(
        id=5,
        coord=GeoCoordinate(lng=1.0, lat=-1.0),
        ways=[3],
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    6: OsmNode(
        id=6,
        coord=GeoCoordinate(lng=0.0, lat=1.0),
        ways=[4],
        metadata={"version": 1, "hd_edges": "[]"},
    ),
}

base_ways = {
    1: Way(
        id=1,
        nodes=[1, 2, 3],
        tags={"version": 1, "highway": "primary", "oneway": "yes"},
    ),
    2: Way(
        id=2, nodes=[4, 1], tags={"version": 1, "highway": "primary", "oneway": "yes"}
    ),
    3: Way(
        id=3, nodes=[3, 5], tags={"version": 1, "highway": "primary", "oneway": "yes"}
    ),
    4: Way(id=4, nodes=[2, 6], tags={"version": 1, "highway": "primary"}),
}

base_relations = {
    (4, (1, 2, 3), 5): Relation(
        1,
        from_way=2,
        from_node=1,
        via=ViaWays((1, 2, 3), ways=[1]),
        to_way=3,
        to_node=5,
        tags={"type": "restriction", "restriction": "no_u_turn", "version": 1},
    ),
    (6, 2, 3): Relation(
        2,
        from_way=4,
        from_node=6,
        via=ViaNode(2),
        to_way=1,
        to_node=3,
        tags={"type": "restriction", "restriction": "no_left_turn", "version": 1},
    ),
}

base_data = Mock(nodes=base_nodes, ways=base_ways, relations=base_relations)

fake_mask = Mask(
    nodes={1, 2, 3, 4, 5},
    edges={(1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (4, 5), (5, 1)},
    relations={(1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 1), (3, 2, 1), (5, 1, 2)},
    hd_mapping={},
)

expected_nodes = base_nodes

expected_ways = {
    1: Way(id=1, nodes=[1, 2], tags={"highway": "primary", "oneway": "yes"}),
    2: Way(id=2, nodes=[4, 1], tags={"highway": "primary", "oneway": "yes"}),
    3: Way(id=3, nodes=[3, 5], tags={"highway": "primary", "oneway": "yes"}),
    4: Way(id=4, nodes=[2, 6], tags={"highway": "primary"}),
    5: Way(id=5, nodes=[2, 3], tags={"highway": "primary", "oneway": "yes"}),
}

expected_relations = {
    (4, (1, 2, 3), 5): Relation(
        1,
        from_way=2,
        from_node=1,
        via=ViaWays((1, 2, 3), ways=[1, 5]),
        to_way=3,
        to_node=5,
        tags={"type": "restriction", "restriction": "no_u_turn"},
    ),
    (6, 2, 3): Relation(
        2,
        from_way=4,
        from_node=6,
        via=ViaNode(2),
        to_way=5,
        to_node=3,
        tags={"type": "restriction", "restriction": "no_left_turn"},
    ),
}

expected_data = Mock(
    nodes=expected_nodes, ways=expected_ways, relations=expected_relations
)
