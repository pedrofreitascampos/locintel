from das.routing.core.datamodel.geo import Geometry, GeoCoordinate
from das.routing.graphs.datamodel.jurbey import Path

from tests.base_fixture import coordinates, graph

graph = graph

expected_paths_edges = [
    [(4, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 0)],
    [(6, 7), (7, 8), (8, 9), (9, 10), (10, 0), (0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 6), (6, 15)],
    [(2, 3), (3, 4), (4, 6), (6, 7), (7, 8), (8, 2), (2, 16)],
    [(2, 3), (3, 4), (4, 6), (6, 7), (7, 8), (8, 11), (11, 13)],
    [(14, 12), (12, 9), (9, 10), (10, 0), (0, 1), (1, 2), (2, 3)],
    [(9, 10), (10, 0), (0, 1), (1, 2), (2, 3), (3, 17), (17, 18)],
]

expected_paths = []
for path_edges in expected_paths_edges:
    path = Path(
        geometry=Geometry(
            [
                GeoCoordinate(lat=coordinates[node_1].lat, lng=coordinates[node_1].lng)
                for node_1, node_2 in path_edges
            ]
        )
    )

    # Adds the last coordinate for last node
    path.geometry.coords = path.geometry.coords + [
        GeoCoordinate(
            lat=coordinates[path_edges[-1][1]].lat,
            lng=coordinates[path_edges[-1][1]].lng,
        )
    ]

    expected_paths.append(path)
