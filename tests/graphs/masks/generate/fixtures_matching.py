from copy import deepcopy

from locintel.core.datamodel.geo import GeoCoordinate, Geometry
from locintel.graphs.datamodel.jurbey import Path
from locintel.graphs.masks.generate.matching import RouteMatchingMaskGenerator
from locintel.graphs.processing.paths import PathsGenerator
from locintel.services.matching import MapboxMatcher

import pytest
from unittest.mock import Mock

fake_nodes_1 = {
    3630503033,
    65665981,
    65485527,
    3633745188,
    65457254,
    3633745189,
    65658106,
}

fake_nodes_2 = {65485527, 3633745188, 65457254, 3633745189, 65658106}

fake_edges_1 = {
    (3630503033, 65665981),
    (65665981, 65485527),
    (65485527, 3633745188),
    (3633745188, 65457254),
}

fake_edges_2 = {
    (65485527, 3633745188),
    (3633745188, 65457254),
    (65457254, 3633745189),
    (3633745189, 65658106),
}

fake_relations_1 = {
    (3630503033, 65665981, 65485527),
    (65665981, 65485527, 3633745188),
    (65485527, 3633745188, 65457254),
}

fake_relations_2 = {
    (65485527, 3633745188, 65457254),
    (3633745188, 65457254, 3633745189),
    (65457254, 3633745189, 65658106),
}


fake_decompose_from_match = [
    (fake_nodes_1, fake_edges_1, fake_relations_1),
    (fake_nodes_2, fake_edges_2, fake_relations_2),
]

expected_edges = deepcopy(fake_edges_1)
expected_edges.update(fake_edges_2)

expected_nodes = deepcopy(fake_nodes_1)
expected_nodes.update(fake_nodes_2)

expected_relations = deepcopy(fake_relations_1)
expected_relations.update(fake_relations_2)

expected_hd_mapping = {
    3630503033: {1},
    65665981: {1},
    65485527: {1, 2},
    3633745188: {1, 2, 3},
    65457254: {2, 3},
    3633745189: {3},
    65658106: {3},
}


@pytest.fixture
def mock_mapbox_route_matching(mocker):
    mock_match_1 = Mock()
    mock_match_2 = Mock()
    mock_matches = [mock_match_1, mock_match_2]
    mock_calculate = mocker.Mock(side_effect=mock_matches)
    mocker.patch.object(MapboxMatcher, "calculate", mock_calculate)
    return mock_matches, mock_calculate


@pytest.fixture
def mock_path_generator(mocker):
    paths = [
        Path(
            geometry=Geometry(
                [
                    GeoCoordinate(lat=0, lng=0),
                    GeoCoordinate(lat=1, lng=0),
                    GeoCoordinate(lat=2, lng=0),
                ]
            ),
            edges=[[1, 2]],
        ),
        Path(
            geometry=Geometry(
                [
                    GeoCoordinate(lat=1, lng=0),
                    GeoCoordinate(lat=2, lng=0),
                    GeoCoordinate(lat=3, lng=0),
                ]
            ),
            edges=[[2, 3]],
        ),
    ]
    generate_mock = Mock(return_value=paths)
    mocker.patch.object(PathsGenerator, "generate", generate_mock)
    return paths, generate_mock


@pytest.fixture
def mock_decompose_mock(mocker):
    decompose_match_mock = Mock(side_effect=fake_decompose_from_match)
    mocker.patch.object(
        RouteMatchingMaskGenerator, "_decompose_match", decompose_match_mock
    )
    return decompose_match_mock
