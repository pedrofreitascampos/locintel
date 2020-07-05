from locintel.core.datamodel.routing import RoutePlan, Route

from tests.fixtures.routing import *
from tests.fixtures.geo import *
from tests.fixtures.testing import *


class TestWaypoint(object):
    def test_waypoint(self, test_coordinates):
        lat, lng = test_coordinates[:2]

        result = Waypoint(lat, lng)

        assert isinstance(result, Waypoint)
        assert result.lat == lat
        assert result.lng == lng

    def test_invalid_coordinate_type_raises_type_error(self):
        with pytest.raises(TypeError):
            Waypoint(10.0, "invalid")

    def test_accepts_kind(self, test_coordinates):
        result = Waypoint(*test_coordinates[:2], kind="VIA")
        assert result.kind == "VIA"

    def test_invalid_kind_raises_value_error(self, test_coordinates):
        with pytest.raises(ValueError):
            Waypoint(*test_coordinates[:2], kind="INVALID_KIND")

    def test_accepts_snap_policy(self, test_coordinates):
        result = Waypoint(*test_coordinates[:2], snap="FUZZY")
        assert result.snap == "FUZZY"

    def test_invalid_snap_policy_raises_value_error(self, test_coordinates):
        with pytest.raises(ValueError):
            Waypoint(*test_coordinates[:2], snap="INVALID_SNAP")

    def test_from_geocoordinate(self, test_coordinates, mock_geocoordinates):
        geocoordinate = mock_geocoordinates[0]
        result = Waypoint.from_geocoordinate(geocoordinate)

        assert isinstance(result, Waypoint)
        assert result.lat == test_coordinates[0]
        assert result.lng == test_coordinates[1]

    def test_to_geocoordinate(self, test_coordinates):
        lat, lng = test_coordinates[:2]
        waypoint = Waypoint(lat, lng)

        result = waypoint.to_geocoordinate()

        assert isinstance(result, GeoCoordinate)
        assert result.lat == lat
        assert result.lng == lng


class TestRoutePlan(object):
    def test_route_plan(self, test_waypoints):
        waypoint_1, waypoint_2 = test_waypoints
        result = RoutePlan(waypoint_1, waypoint_2)

        assert isinstance(result, RoutePlan)
        assert result.start == waypoint_1
        assert result.end == waypoint_2

    def test_invalid_start_type_raises_type_error(self):
        with pytest.raises(TypeError):
            RoutePlan("invalid_type", Waypoint(10, 2))

    def test_via_start_point_raises_value_error(self):
        with pytest.raises(ValueError):
            RoutePlan(Waypoint(9, 7, kind="VIA"), Waypoint(10, 2))

    def test_invalid_end_type_raises_type_error(self):
        with pytest.raises(TypeError):
            RoutePlan(Waypoint(10, 2), "invalid_type")

    def test_via_end_point_raises_value_error(self):
        with pytest.raises(ValueError):
            RoutePlan(Waypoint(10, 2), Waypoint(9, 7, kind="VIA"))

    def test_intermediate_waypoints(self, test_waypoints):
        intermediate_waypoints = [Waypoint(40, 50), Waypoint(10, 2)]
        result = RoutePlan(
            *test_waypoints, intermediate_waypoints=intermediate_waypoints
        )

        assert result.start == test_waypoints[0]
        assert result.end == test_waypoints[1]
        assert result.intermediate_waypoints == intermediate_waypoints

    def test_invalid_intermediate_waypoint_type_raises_type_error(self, test_waypoints):
        with pytest.raises(TypeError):
            RoutePlan(
                *test_waypoints,
                intermediate_waypoints=[Waypoint(10, 20), "INVALID", Waypoint(30, 10)]
            )

    def test_accepts_vehicle_type(self, test_waypoints):
        result = RoutePlan(*test_waypoints, vehicle="PEDESTRIAN")

        assert result.vehicle == "PEDESTRIAN"

    def test_invalid_vehicle_type_raises_value_error(self, test_waypoints):
        with pytest.raises(ValueError):
            RoutePlan(*test_waypoints, vehicle="INVALID_VEHICLE")

    def test_accepts_profile(self, test_waypoints):
        result = RoutePlan(*test_waypoints, strategy="SHORTEST")

        assert result.strategy == "SHORTEST"

    def test_invalid_profile_raises_value_error(self, test_waypoints):
        with pytest.raises(ValueError):
            RoutePlan(*test_waypoints, strategy="INVALID_PROFILE")

    def test_get_waypoints(self, test_waypoints):
        start, end = test_waypoints
        intermediate_waypoints = [Waypoint(10, 20), Waypoint(30, 10)]
        route_plan = RoutePlan(
            start, end, intermediate_waypoints=intermediate_waypoints
        )
        result = route_plan.get_waypoints()

        assert len(result) == 4
        assert result == (
            start,
            intermediate_waypoints[0],
            intermediate_waypoints[1],
            end,
        )

    def test_get_waypoints_returns_2_when_no_intermediate_waypoints(
        self, test_waypoints
    ):
        route_plan = RoutePlan(*test_waypoints)
        result = route_plan.get_waypoints()

        assert len(result) == 2
        assert result == test_waypoints


class TestRoute(object):
    def test_route(self, test_geometry):
        distance = 10.0
        duration = 5.0
        geometry = test_geometry

        result = Route(geometry, distance, duration)

        assert isinstance(result, Route)
        assert result.geometry == test_geometry
        assert result.distance == distance
        assert result.duration == duration

    def test_invalid_geometry_raises_type_error(self):
        with pytest.raises(TypeError):
            Route(geometry="INVALID_TYPE", distance=10, duration=50)

    def test_invalid_distance_type_raises_type_error(self, test_geometry):
        with pytest.raises(TypeError):
            Route(geometry=test_geometry, distance="INVALID_TYPE", duration=50)

    def test_negative_distance_raises_value_error(self, test_geometry):
        with pytest.raises(ValueError):
            Route(geometry=test_geometry, distance=-50, duration=50)

    def test_invalid_duration_type_raises_type_error(self, test_geometry):
        with pytest.raises(TypeError):
            Route(geometry=test_geometry, distance=10, duration="INVALID_TYPE")

    def test_negative_duration_raises_value_error(self, test_geometry):
        with pytest.raises(ValueError):
            Route(geometry=test_geometry, distance=20, duration=-50)

    def test_route_from_database_document(self, mocker):
        route_plan_from_database_document_mock = Mock(
            return_value=expected_route_plan_mock
        )
        mocker.patch(
            "locintel.core.datamodel.routing.RoutePlan.from_database_document",
            route_plan_from_database_document_mock,
        )
        expected_geometry_mock = Mock(
            coords=[Mock(lat=lat, lng=lng, alt=0.0) for lng, lat in expected_geometry]
        )

        result = Route.from_database_document(route_mapbox)

        assert isinstance(result, Route)
        assert result.distance == expected_distance
        assert result.duration == expected_duration
        assert result.geometry == expected_geometry_mock
        assert result.metadata == expected_metadata
        route_plan_from_database_document_mock.assert_called_with(expected_route_plan)
