from locintel.services.matching import MapboxMatcher

from tests.fixtures_matching import setup_mapbox_matcher_environment

import pytest
from unittest.mock import Mock


class TestMatching:
    matcher = MapboxMatcher(endpoint="http://localhost:5000/v1/match")
    coords = [[0, 0], [1, 0], [2, 0]]
    plan = Mock(points=[Mock(lat=coord[0], lng=coord[1]) for coord in coords])

    def test_calculate(self, setup_mapbox_matcher_environment):
        expected_match = setup_mapbox_matcher_environment["expected_match"]
        match = self.matcher.calculate(self.plan)

        assert match.duration == expected_match.duration
        assert match.distance == expected_match.distance
        assert len(match.geometry.coords) == len(expected_match.geometry.coords)
        for match_coord, expected_match_coord in zip(
            match.geometry.coords, expected_match.geometry.coords
        ):
            assert match_coord.lat == expected_match_coord.lat
            assert match_coord.lng == expected_match_coord.lng

        assert match.metadata["confidence"] == expected_match.metadata["confidence"]
        assert (
            match.metadata["max_snap_distance"]
            == expected_match.metadata["max_snap_distance"]
        )
        assert (
            match.metadata["failed_points"] == expected_match.metadata["failed_points"]
        )
        assert match.metadata["raw"] == expected_match.metadata["raw"]

    #  TODO: split tests into calculate vs adapter
