from das.routing.core.datamodel.geo import GeoCoordinate
from das.routing.graphs.datamodel.jurbey import Mask
from das.routing.graphs.datamodel.osm import Node as OsmNode, Way, Relation, ViaNode

from unittest.mock import Mock

"""
============================================================

    Test Case 2 - New turn restrictions are created based on
                  the mask

                    4
                    |
                1---2-->3                                    
                    |
                    v
                    5

nodes:        (1, 2, 3, 4, 5)

ways:         1: (1, 2, 3, {"oneway": true})
              2: (4, 2, 5, {"oneway": true})

restrictions: None

============================================================              
"""

base_nodes = {
    1: OsmNode(
        id=1,
        coord=GeoCoordinate(lng=-1.0, lat=0.0),
        ways=[],
        metadata={"hd_edges": "[]"},
    ),
    2: OsmNode(
        id=2,
        coord=GeoCoordinate(lng=0.0, lat=0.0),
        ways=[],
        metadata={"hd_edges": "[]"},
    ),
    3: OsmNode(
        id=3,
        coord=GeoCoordinate(lng=1.0, lat=0.0),
        ways=[],
        metadata={"hd_edges": "[]"},
    ),
    4: OsmNode(
        id=4,
        coord=GeoCoordinate(lng=0.0, lat=1.0),
        ways=[],
        metadata={"hd_edges": "[]"},
    ),
    5: OsmNode(
        id=5,
        coord=GeoCoordinate(lng=0.0, lat=-1.0),
        ways=[],
        metadata={"hd_edges": "[]"},
    ),
}
base_ways = {
    1: Way(id=1, nodes=[1, 2, 3], tags={"highway": "primary", "oneway": "yes"}),
    2: Way(id=2, nodes=[4, 2, 5], tags={"highway": "primary", "oneway": "yes"}),
}
base_relations = {}

base_data = Mock(nodes=base_nodes, ways=base_ways, relations=base_relations)

fake_mask = Mask(
    nodes={1, 2, 3, 4, 5},
    edges={(1, 2), (2, 3), (4, 2), (2, 5)},
    relations={(1, 2, 3), (4, 2, 5), (4, 2, 1)},
    hd_mapping={},
)

expected_nodes = {
    1: OsmNode(
        id=1,
        coord=GeoCoordinate(lng=-1.0, lat=0.0),
        ways=[1],
        metadata={"hd_edges": "[]"},
    ),
    2: OsmNode(
        id=2,
        coord=GeoCoordinate(lng=0.0, lat=0.0),
        ways=[1, 2],
        metadata={"hd_edges": "[]"},
    ),
    3: OsmNode(
        id=3,
        coord=GeoCoordinate(lng=1.0, lat=0.0),
        ways=[1],
        metadata={"hd_edges": "[]"},
    ),
    4: OsmNode(
        id=4,
        coord=GeoCoordinate(lng=0.0, lat=1.0),
        ways=[2],
        metadata={"hd_edges": "[]"},
    ),
    5: OsmNode(
        id=5,
        coord=GeoCoordinate(lng=0.0, lat=-1.0),
        ways=[2],
        metadata={"hd_edges": "[]"},
    ),
}

expected_ways = {
    1: Way(id=1, nodes=[1, 2, 3], tags={"highway": "primary", "oneway": "yes"}),
    2: Way(id=2, nodes=[4, 2, 5], tags={"highway": "primary", "oneway": "yes"}),
}

expected_relations = {
    (1, 2, 5): Relation(
        1,
        from_way=1,
        from_node=1,
        via=ViaNode(2),
        to_way=2,
        to_node=5,
        tags={"type": "restriction", "restriction": "no_right_turn", "version": 1},
    ),
    (4, 2, 3): Relation(
        2,
        from_way=2,
        from_node=4,
        via=ViaNode(2),
        to_way=1,
        to_node=3,
        tags={"type": "restriction", "restriction": "no_left_turn", "version": 1},
    ),
}

expected_data = Mock(
    nodes=expected_nodes, ways=expected_ways, relations=expected_relations
)
