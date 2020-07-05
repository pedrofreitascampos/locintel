import pytest

from locintel.core.datamodel.routing import Waypoint


@pytest.fixture
def test_waypoints():
    #  TODO: mock instead
    return Waypoint(10, 0), Waypoint(20, 15)
