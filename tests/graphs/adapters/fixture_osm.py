from das.routing.core.datamodel.geo import GeoCoordinate, Geometry
from das.routing.graphs.datamodel.jurbey import Edge, Node
from das.routing.graphs.datamodel.types import (
    EdgeType,
    RoadClass,
    RoadAccessibility,
    VehicleType,
)

from unittest.mock import Mock

"""
========================================================

        OSM Base Graph - see fixture_osm.osm for source OSM file 

            6     
            |   7       15  14
            ↓   ↑       |   |
        1---2---3---4---5---11
            ↓       |       |
            8       10      |
            ↓       |       |
            9       13------12                                       

nodes:        (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)

ways:         1: (1, 2, 3, 4, {})
              2: (4, 5, 11, {})
              3: (6, 2, 8, 9, {"oneway": "yes"})
              4: (3, 7, {"oneway": "yes"})
              5: (4, 10, 13, 12, 11, {})
              6: (5, 15, {})
              7: (11, 14, {})

restrictions: 1: (w5@from, n4@via, w2@to)
              2: (w7@from, w2@via, w5@to)

========================================================

"""
expected_nodes = {
    1: {
        "data": Node(
            id=1,
            coord=GeoCoordinate(lng=-1, lat=0),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    2: {
        "data": Node(
            id=2,
            coord=GeoCoordinate(lng=0, lat=0),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    3: {
        "data": Node(
            id=3,
            coord=GeoCoordinate(lng=1, lat=0),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    4: {
        "data": Node(
            id=4,
            coord=GeoCoordinate(lng=2, lat=0),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    5: {
        "data": Node(
            id=5,
            coord=GeoCoordinate(lng=3, lat=0),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    6: {
        "data": Node(
            id=6,
            coord=GeoCoordinate(lng=0, lat=2),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    7: {
        "data": Node(
            id=7,
            coord=GeoCoordinate(lng=1, lat=1),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    8: {
        "data": Node(
            id=8,
            coord=GeoCoordinate(lng=0, lat=-1),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    9: {
        "data": Node(
            id=9,
            coord=GeoCoordinate(lng=0, lat=-2),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    10: {
        "data": Node(
            id=10,
            coord=GeoCoordinate(lng=2, lat=-1),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    11: {
        "data": Node(
            id=11,
            coord=GeoCoordinate(lng=4, lat=0),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    12: {
        "data": Node(
            id=12,
            coord=GeoCoordinate(lng=4, lat=-2),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    13: {
        "data": Node(
            id=13,
            coord=GeoCoordinate(lng=2, lat=-2),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    14: {
        "data": Node(
            id=14,
            coord=GeoCoordinate(lng=4, lat=1),
            metadata={"version": 1, "hd_edges": []},
        )
    },
    15: {
        "data": Node(
            id=15,
            coord=GeoCoordinate(lng=3, lat=1),
            metadata={"version": 1, "hd_edges": []},
        )
    },
}

expected_edges = {
    1: {
        2: {
            "way": [1],
            "speed": 65,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=1,
                to_node=2,
                geometry=Geometry(
                    [expected_nodes[1]["data"].coord, expected_nodes[2]["data"].coord]
                ),
                road_class=RoadClass.MajorRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "primary"},
            ),
        }
    },
    2: {
        1: {
            "way": [1],
            "speed": 65,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=2,
                to_node=1,
                geometry=Geometry(
                    [expected_nodes[2]["data"].coord, expected_nodes[1]["data"].coord]
                ),
                road_class=RoadClass.MajorRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "primary"},
            ),
        },
        3: {
            "way": [1],
            "speed": 65,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=2,
                to_node=3,
                geometry=Geometry(
                    [expected_nodes[2]["data"].coord, expected_nodes[3]["data"].coord]
                ),
                road_class=RoadClass.MajorRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "primary"},
            ),
        },
        8: {
            "way": [3],
            "speed": 65,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=2,
                to_node=8,
                geometry=Geometry(
                    [expected_nodes[2]["data"].coord, expected_nodes[8]["data"].coord]
                ),
                road_class=RoadClass.MajorRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "primary", "oneway": "yes"},
            ),
        },
    },
    3: {
        2: {
            "way": [1],
            "speed": 65,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=3,
                to_node=2,
                geometry=Geometry(
                    [expected_nodes[3]["data"].coord, expected_nodes[2]["data"].coord]
                ),
                road_class=RoadClass.MajorRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "primary"},
            ),
        },
        4: {
            "way": [1],
            "speed": 65,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=3,
                to_node=4,
                geometry=Geometry(
                    [expected_nodes[3]["data"].coord, expected_nodes[4]["data"].coord]
                ),
                road_class=RoadClass.MajorRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "primary"},
            ),
        },
        7: {
            "way": [4],
            "speed": 25,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=3,
                to_node=7,
                geometry=Geometry(
                    [expected_nodes[3]["data"].coord, expected_nodes[7]["data"].coord]
                ),
                road_class=RoadClass.LocalRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "residential", "oneway": "yes"},
            ),
        },
    },
    4: {
        3: {
            "way": [1],
            "speed": 65,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=4,
                to_node=3,
                geometry=Geometry(
                    [expected_nodes[4]["data"].coord, expected_nodes[3]["data"].coord]
                ),
                road_class=RoadClass.MajorRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "primary"},
            ),
        },
        5: {
            "way": [2],
            "speed": 65,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=4,
                to_node=5,
                geometry=Geometry(
                    [expected_nodes[4]["data"].coord, expected_nodes[5]["data"].coord]
                ),
                road_class=RoadClass.MajorRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "primary"},
            ),
        },
        10: {
            "way": [5],
            "speed": 25,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=4,
                to_node=10,
                geometry=Geometry(
                    [expected_nodes[4]["data"].coord, expected_nodes[10]["data"].coord]
                ),
                road_class=RoadClass.LocalRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "residential"},
            ),
        },
    },
    5: {
        4: {
            "way": [2],
            "speed": 65,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=5,
                to_node=4,
                geometry=Geometry(
                    [expected_nodes[5]["data"].coord, expected_nodes[4]["data"].coord]
                ),
                road_class=RoadClass.MajorRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "primary"},
            ),
        },
        11: {
            "way": [2],
            "speed": 65,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=5,
                to_node=11,
                geometry=Geometry(
                    [expected_nodes[5]["data"].coord, expected_nodes[11]["data"].coord]
                ),
                road_class=RoadClass.MajorRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "primary"},
            ),
        },
        15: {
            "way": [6],
            "speed": 25,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=5,
                to_node=15,
                geometry=Geometry(
                    [expected_nodes[5]["data"].coord, expected_nodes[15]["data"].coord]
                ),
                road_class=RoadClass.LocalRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "residential"},
            ),
        },
    },
    6: {
        2: {
            "way": [3],
            "speed": 65,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=6,
                to_node=2,
                geometry=Geometry(
                    [expected_nodes[6]["data"].coord, expected_nodes[2]["data"].coord]
                ),
                road_class=RoadClass.MajorRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "primary", "oneway": "yes"},
            ),
        }
    },
    8: {
        9: {
            "way": [3],
            "speed": 65,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=8,
                to_node=9,
                geometry=Geometry(
                    [expected_nodes[8]["data"].coord, expected_nodes[9]["data"].coord]
                ),
                road_class=RoadClass.MajorRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "primary", "oneway": "yes"},
            ),
        }
    },
    10: {
        4: {
            "way": [5],
            "speed": 25,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=10,
                to_node=4,
                geometry=Geometry(
                    [expected_nodes[10]["data"].coord, expected_nodes[4]["data"].coord]
                ),
                road_class=RoadClass.LocalRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "residential"},
            ),
        },
        13: {
            "way": [5],
            "speed": 25,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=10,
                to_node=13,
                geometry=Geometry(
                    [expected_nodes[10]["data"].coord, expected_nodes[13]["data"].coord]
                ),
                road_class=RoadClass.LocalRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "residential"},
            ),
        },
    },
    11: {
        5: {
            "way": [2],
            "speed": 65,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=11,
                to_node=5,
                geometry=Geometry(
                    [expected_nodes[11]["data"].coord, expected_nodes[5]["data"].coord]
                ),
                road_class=RoadClass.MajorRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "primary"},
            ),
        },
        12: {
            "way": [5],
            "speed": 25,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=11,
                to_node=12,
                geometry=Geometry(
                    [expected_nodes[11]["data"].coord, expected_nodes[12]["data"].coord]
                ),
                road_class=RoadClass.LocalRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "residential"},
            ),
        },
        14: {
            "way": [7],
            "speed": 25,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=11,
                to_node=14,
                geometry=Geometry(
                    [expected_nodes[11]["data"].coord, expected_nodes[14]["data"].coord]
                ),
                road_class=RoadClass.LocalRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "residential"},
            ),
        },
    },
    12: {
        11: {
            "way": [5],
            "speed": 25,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=12,
                to_node=11,
                geometry=Geometry(
                    [expected_nodes[12]["data"].coord, expected_nodes[11]["data"].coord]
                ),
                road_class=RoadClass.LocalRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "residential"},
            ),
        },
        13: {
            "way": [5],
            "speed": 25,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=12,
                to_node=13,
                geometry=Geometry(
                    [expected_nodes[12]["data"].coord, expected_nodes[13]["data"].coord]
                ),
                road_class=RoadClass.LocalRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "residential"},
            ),
        },
    },
    13: {
        10: {
            "way": [5],
            "speed": 25,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=13,
                to_node=10,
                geometry=Geometry(
                    [expected_nodes[13]["data"].coord, expected_nodes[10]["data"].coord]
                ),
                road_class=RoadClass.LocalRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "residential"},
            ),
        },
        12: {
            "way": [5],
            "speed": 25,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=13,
                to_node=12,
                geometry=Geometry(
                    [expected_nodes[13]["data"].coord, expected_nodes[12]["data"].coord]
                ),
                road_class=RoadClass.LocalRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "residential"},
            ),
        },
    },
    14: {
        11: {
            "way": [7],
            "speed": 25,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=14,
                to_node=11,
                geometry=Geometry(
                    [expected_nodes[14]["data"].coord, expected_nodes[11]["data"].coord]
                ),
                road_class=RoadClass.LocalRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "residential"},
            ),
        }
    },
    15: {
        5: {
            "way": [6],
            "speed": 25,
            "rate": 1,
            "direction": 0,
            "data": Edge(
                type=EdgeType.LANE_STRAIGHT,
                from_node=15,
                to_node=5,
                geometry=Geometry(
                    [expected_nodes[15]["data"].coord, expected_nodes[5]["data"].coord]
                ),
                road_class=RoadClass.LocalRoad,
                road_accessibility=RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={"highway": "residential"},
            ),
        }
    },
    # 9 and 7 aren't connected but are still included in the _adjlist of networkx as empty dicts
    7: {},
    9: {},
}

expected_graph = Mock(nodes=expected_nodes, edges=expected_edges)
