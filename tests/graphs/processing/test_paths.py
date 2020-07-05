import builtins

from das.routing.graphs.processing.paths import PathsGenerator

import pytest
from tests.processing.fixtures_paths import expected_paths, graph


class TestGeneratePaths(object):
    @pytest.mark.skip
    def test_generate_paths(self):
        paths_generator = PathsGenerator(graph)

        paths = paths_generator.generate()

        assert paths == expected_paths

    @pytest.mark.skip
    def test_export_geometries(self, mocker):
        stub = mocker.stub()
        mocker.patch.object(builtins, "open", stub)
        filename = "tests/geometries.geojson"

        PathsGenerator.export_geometries(expected_paths, filename)

        stub.assert_called_once_with(filename, "wb")
