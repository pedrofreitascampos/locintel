from importlib import import_module

from locintel.graphs.masks.apply.osm import ApplyMaskOsmMixin

import pytest

from tests.masks.apply.fixture_base_case import (
    base_nodes as base_case_base_nodes,
    base_ways as base_case_base_ways,
    base_relations as base_case_base_relations,
    fake_mask as base_case_fake_mask,
    expected_data as base_case_expected_data,
)


def get_variables(test_case):
    module = import_module(f".{test_case}", package="tests.masks.apply")
    fake_mask = getattr(module, "fake_mask")
    base_data = getattr(module, "base_data")
    expected_data = getattr(module, "expected_data")
    return fake_mask, base_data, expected_data


class TestApplyMaskOsm:
    fixtures = [
        "fixture_base_case",
        "fixture_ways_get_split_and_referring_ways_are_updated",
        "fixture_ways_get_split_and_viaways_are_updated",
        "fixture_relations_with_edges_outside_mask_get_deleted",
        "fixture_nodes_in_way_get_filtered_out",
        "fixture_new_turn_restrictions_are_created",
        "fixture_bidirectional_way_becomes_onedirectional",
        "fixture_ways_get_split_and_nodes_are_in_right_order",
        "fixture_way_gets_split_into_multiple_ways",
    ]

    @pytest.mark.parametrize(
        "fake_mask,base_data,expected_data",
        [pytest.param(*get_variables(fixture), id=fixture) for fixture in fixtures],
    )
    def test_apply_mask(self, fake_mask, base_data, expected_data):
        apply_mask = ApplyMaskOsmMixin()

        # assume apply_file has been ran by OsmAdapter, nodes, ways, relations are already populated
        apply_mask.nodes = base_data.nodes
        apply_mask.ways = base_data.ways
        apply_mask.relations = base_data.relations

        apply_mask.apply_mask(fake_mask)

        assert apply_mask.nodes == expected_data.nodes
        assert apply_mask.ways == expected_data.ways
        assert apply_mask.relations == expected_data.relations

    @pytest.mark.skip
    def test_node(self):
        apply_mask = ApplyMaskOsmMixin()
        apply_mask.apply_mask(base_case_fake_mask)
        for node in base_case_base_nodes:
            apply_mask.node(node)

        assert apply_mask.G.nodes == base_case_expected_data.nodes

    @pytest.mark.skip
    def test_way(self):
        apply_mask = ApplyMaskOsmMixin()
        apply_mask.apply_mask(base_case_fake_mask)
        for way in base_case_base_ways:
            apply_mask.way(way)

        assert apply_mask.G.ways == base_case_expected_data.ways

    @pytest.mark.skip
    def test_relation(self):
        apply_mask = ApplyMaskOsmMixin()
        apply_mask.apply_mask(base_case_fake_mask)
        apply_mask.G.nodes = base_case_expected_data.nodes
        apply_mask.G.ways = base_case_expected_data.ways

        for relation in base_case_base_relations:
            apply_mask.relation(relation)

        assert apply_mask.G.relations == base_case_expected_data.relations
