from das.routing.core.datamodel.geo import GeoCoordinate
from das.routing.graphs.datamodel.jurbey import Mask
from das.routing.graphs.datamodel.osm import Node as OsmNode, Way

from unittest.mock import Mock

"""
============================================================

    Test Case 4 - Bi-directional way has differing 
        edges in each direction:

         -> ways get split accordingly
         -> nodes get appended in the right order when they are reversed


            ---1-------2---
               |       |
               5       |
               |       |
               4-------3       



nodes:        (1, 2, 3, 4, 5)

ways:         1: (1, 2, {})
              2: (1, 5, 4, 3, 2, {})

restrictions: None

============================================================              
"""

base_nodes = {
    1: OsmNode(
        id=1,
        coord=GeoCoordinate(lng=-2.0, lat=0.0),
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
        coord=GeoCoordinate(lng=0.0, lat=-2.0),
        ways=[],
        metadata={"hd_edges": "[]"},
    ),
    4: OsmNode(
        id=4,
        coord=GeoCoordinate(lng=-2.0, lat=-2.0),
        ways=[],
        metadata={"hd_edges": "[]"},
    ),
    5: OsmNode(
        id=5,
        coord=GeoCoordinate(lng=-2.0, lat=-1.0),
        ways=[],
        metadata={"hd_edges": "[]"},
    ),
}
base_ways = {
    1: Way(id=1, nodes=[1, 2], tags={"highway": "primary"}),
    2: Way(id=2, nodes=[1, 5, 4, 3, 2], tags={"highway": "primary"}),
}
base_relations = {}

base_data = Mock(nodes=base_nodes, ways=base_ways, relations=base_relations)

fake_mask = Mask(
    nodes={1, 2, 3, 4, 5},
    edges={(1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (4, 5), (5, 1)},
    relations={(1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 1), (3, 2, 1), (5, 1, 2)},
    hd_mapping={},
)

expected_ways = {
    1: Way(id=1, nodes=[1, 2], tags={"highway": "primary"}),
    2: Way(id=2, nodes=[3, 2], tags={"highway": "primary"}),
    3: Way(id=3, nodes=[3, 4, 5, 1], tags={"highway": "primary", "oneway": "yes"}),
}
expected_nodes = {
    1: OsmNode(
        id=1,
        coord=GeoCoordinate(lng=-2.0, lat=0.0),
        ways=[1, 3],
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
        coord=GeoCoordinate(lng=0.0, lat=-2.0),
        ways=[2, 3],
        metadata={"hd_edges": "[]"},
    ),
    4: OsmNode(
        id=4,
        coord=GeoCoordinate(lng=-2.0, lat=-2.0),
        ways=[3],
        metadata={"hd_edges": "[]"},
    ),
    5: OsmNode(
        id=5,
        coord=GeoCoordinate(lng=-2.0, lat=-1.0),
        ways=[3],
        metadata={"hd_edges": "[]"},
    ),
}
expected_relations = {}

expected_data = Mock(
    nodes=expected_nodes, ways=expected_ways, relations=expected_relations
)
