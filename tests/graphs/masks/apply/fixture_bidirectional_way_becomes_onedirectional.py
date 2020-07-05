from das.routing.core.datamodel.geo import GeoCoordinate
from das.routing.graphs.datamodel.jurbey import Mask
from das.routing.graphs.datamodel.osm import Node as OsmNode, Way

from unittest.mock import Mock

"""
============================================================

    Test Case 3 - Bi-directional way becomes one directional


                1---2---3                                   
                    

nodes:        (1, 2, 3)

ways:         1: (1, 2, 3, {})

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
}

base_ways = {1: Way(id=1, nodes=[1, 2, 3], tags={"highway": "primary"})}

base_relations = {}

base_data = Mock(nodes=base_nodes, ways=base_ways, relations=base_relations)

fake_mask = Mask(
    nodes={1, 2, 3}, edges={(1, 2), (2, 3)}, relations={(1, 2, 3)}, hd_mapping={}
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

expected_ways = {
    1: Way(id=1, nodes=[1, 2, 3], tags={"highway": "primary", "oneway": "yes"})
}

expected_relations = {}

expected_data = Mock(
    nodes=expected_nodes, ways=expected_ways, relations=expected_relations
)
