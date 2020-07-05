from locintel.graphs.masks.generate.matching import RouteMatchingMaskGenerator

from unittest.mock import Mock

from .fixtures_matching import (
    mock_mapbox_route_matching,
    mock_decompose_mock,
    mock_path_generator,
    expected_edges,
    expected_nodes,
    expected_relations,
    expected_hd_mapping,
)


class TestGraphMatchingMaskGenerator:
    def test_generate(
        self, mock_mapbox_route_matching, mock_path_generator, mock_decompose_mock
    ):
        odd_graph_mock = Mock()
        mask_generator = RouteMatchingMaskGenerator(odd_graph=odd_graph_mock)

        mask = mask_generator.generate()

        assert mask.nodes == expected_nodes
        assert mask.edges == expected_edges
        assert mask.relations == expected_relations
