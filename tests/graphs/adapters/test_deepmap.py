import builtins
import json

from das.routing.graphs.adapters.deepmap import DeepmapAdapter

import pytest

from .fixture_deepmap import (
    deepmap_lane_data,
    expected_graph,
    expected_graph_with_virtual_lanes,
)


@pytest.fixture
def mock_json(mocker):
    load_mock = mocker.Mock(return_value=deepmap_lane_data)
    mocker.patch.object(json, "load", load_mock)
    return load_mock


class TestDeepmapAdapter:
    def test_deepmap_adapter(self, mocker, mock_json):
        deepmap_filename = "deepmap.json"
        stub = mocker.stub()
        mocker.patch.object(builtins, "open", stub)

        adapter = DeepmapAdapter(deepmap_filename)

        assert adapter.data == deepmap_lane_data
        stub.assert_called_once_with(deepmap_filename, "r")

    def test_get_jurbey(self, mocker, mock_json):
        deepmap_filename = "deepmap.json"
        stub = mocker.stub()
        mocker.patch.object(builtins, "open", stub)

        adapter = DeepmapAdapter(deepmap_filename)

        graph = adapter.get_jurbey(add_virtual_lanes=False)

        assert graph.edges == expected_graph.edges
        assert sorted(graph.nodes) == sorted(expected_graph.nodes)

    def test_get_jurbey_with_virtual_lanes(self, mocker, mock_json):
        deepmap_filename = "deepmap.json"
        stub = mocker.stub()
        mocker.patch.object(builtins, "open", stub)
        adapter = DeepmapAdapter(deepmap_filename)

        graph = adapter.get_jurbey(add_virtual_lanes=True)

        assert graph.edges == expected_graph_with_virtual_lanes.edges
        assert sorted(graph.nodes) == sorted(expected_graph_with_virtual_lanes.nodes)
