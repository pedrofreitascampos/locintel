from locintel.core.datamodel.geo import GeoCoordinate
from locintel.graphs.datamodel.jurbey import Mask
from locintel.graphs.datamodel.osm import Node as OsmNode, Way, Relation, ViaNode

from unittest.mock import Mock

"""
============================================================

    Test Case 3 - relations with edges outside 
                  of ODD are deleted

                1   4
                 \  |
                  2 |
                   \|
                    3
                
nodes:        (1, 2, 3, 4)

ways:         1: (1, 2, 3, {})
              2: (4, 3, {})

restrictions: 1: (w1@from, n2@from, n3@via, w2@to, n4@to)

============================================================              
"""

base_nodes = {
    1: OsmNode(
        id=1,
        coord=GeoCoordinate(lng=0.0, lat=0.0),
        ways=[1],
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    2: OsmNode(
        id=2,
        coord=GeoCoordinate(lng=1.0, lat=-1.0),
        ways=[1],
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    3: OsmNode(
        id=3,
        coord=GeoCoordinate(lng=2.0, lat=-2.0),
        ways=[2],
        metadata={"version": 1, "hd_edges": "[]"},
    ),
    4: OsmNode(
        id=4,
        coord=GeoCoordinate(lng=2.0, lat=0.0),
        ways=[2],
        metadata={"version": 1, "hd_edges": "[]"},
    ),
}

base_ways = {
    1: Way(id=1, nodes=[1, 2], tags={"version": 1, "highway": "primary"}),
    2: Way(id=2, nodes=[3, 4], tags={"version": 1, "highway": "primary"}),
}

base_relations = {
    (2, 3, 4): Relation(
        1,
        from_way=1,
        from_node=2,
        via=ViaNode(3),
        to_way=2,
        to_node=4,
        tags={"type": "restriction", "restriction": "no_right_turn", "version": 1},
    )
}

base_data = Mock(nodes=base_nodes, ways=base_ways, relations=base_relations)

fake_mask = Mask(
    nodes={1, 2, 3, 4, 5},
    edges={(1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (4, 5), (5, 1)},
    relations={(1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 1), (3, 2, 1), (5, 1, 2)},
    hd_mapping={},
)

expected_nodes = base_nodes

expected_ways = base_ways

expected_relations = {}

expected_data = Mock(
    nodes=expected_nodes, ways=expected_ways, relations=expected_relations
)
