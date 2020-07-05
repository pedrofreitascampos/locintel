from das.routing.core.datamodel.geo import GeoCoordinate
from das.routing.graphs.datamodel.jurbey import Mask
from das.routing.graphs.datamodel.osm import Node as OsmNode, Way, Relation

from unittest.mock import Mock

"""
============================================================

        Test Case 1 - nodes in way get filtered out 
                      according to mask

                           _________
                          |         |
                1---2---3---4---5   | Mocks inside this box                           
                          |         | have been prefiltered 
                           ---------

nodes:        (1, 2, 3, 4, 5)

ways:         1: (1, 2, 3, 4, 5, {})

restrictions: None

============================================================              
"""

base_nodes = {
    1: OsmNode(
        1, coord=GeoCoordinate(lng=-1.0, lat=0.0), ways=[], metadata={"hd_edges": "[]"}
    ),
    2: OsmNode(
        2, coord=GeoCoordinate(lng=0.0, lat=0.0), ways=[], metadata={"hd_edges": "[]"}
    ),
    3: OsmNode(
        3, coord=GeoCoordinate(lng=1.0, lat=0.0), ways=[], metadata={"hd_edges": "[]"}
    ),
}
base_ways = {1: Way(id=1, nodes=[1, 2, 3, 4, 5], tags={"highway": "primary"})}
base_relations = {}

base_data = Mock(nodes=base_nodes, ways=base_ways, relations=base_relations)

fake_mask = Mask(
    nodes={1, 2, 3},
    edges={(1, 2), (2, 1), (2, 3), (3, 2)},
    relations={(1, 2, 3), (3, 2, 1)},
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
        ways=[1],
        metadata={"hd_edges": "[]"},
    ),
    3: OsmNode(
        id=3,
        coord=GeoCoordinate(lng=1.0, lat=0.0),
        ways=[1],
        metadata={"hd_edges": "[]"},
    ),
}
expected_ways = {1: Way(id=1, nodes=[1, 2, 3], tags={"highway": "primary"})}
expected_relations = {}

expected_data = Mock(
    nodes=expected_nodes, ways=expected_ways, relations=expected_relations
)
