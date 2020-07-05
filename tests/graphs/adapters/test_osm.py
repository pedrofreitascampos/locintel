from locintel.graphs.adapters.osm import OsmAdapter, OsmAdapterWithMask
from locintel.graphs.datamodel.jurbey import Jurbey
from locintel.graphs.masks.apply.osm import ApplyMaskOsmMixin

import pytest
from unittest.mock import Mock

from .fixture_osm import expected_graph


def mock_apply_mask_mixin(cls, graph_return, mixin_return):
    mixin_method_mock = Mock(return_value=mixin_return)
    get_jurbey_mock = Mock(return_value=graph_return)
    cls.mixin_method = mixin_method_mock
    cls.get_jurbey = get_jurbey_mock
    return dict(
        get_jurbey=get_jurbey_mock,
        mixin_method=mixin_method_mock,
        expected_graph=expected_graph,
        mixin_method_return=mixin_return,
    )


class TestOsmAdapter:
    osm_test_map_path = "tests/adapters/fixture_osm.osm"

    def test_get_jurbey(self):
        osm_adapter = OsmAdapter(osm_filename=self.osm_test_map_path)
        graph = osm_adapter.get_jurbey()

        assert isinstance(graph, Jurbey)
        assert graph.nodes(data=True)._nodes == expected_graph.nodes
        assert graph.edges(data=True)._adjdict == expected_graph.edges

    def test_get_jurbey_with_mask(self, mocker):
        mixin_method_return = Mock()
        expected_masked_graph = Mock()
        mocker.patch.object(
            ApplyMaskOsmMixin,
            "__init__",
            side_effect=lambda cls: mock_apply_mask_mixin(
                cls, expected_masked_graph, mixin_method_return
            ),
        )

        osm_adapter = OsmAdapterWithMask(self.osm_test_map_path)
        graph = osm_adapter.get_jurbey()

        assert graph == expected_masked_graph
        assert getattr(osm_adapter, "mixin_method")() == mixin_method_return
