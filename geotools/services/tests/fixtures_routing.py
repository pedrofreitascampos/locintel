from unittest.mock import Mock

import pytest

from das.routing.core.datamodel.geo import Geometry, GeoCoordinate
from das.routing.core.datamodel.routing import Route, RoutePlan, Waypoint
from das.routing.services.routing import DasResponseAdapter, GoogleResponseAdapter
from das.routing.services.matching import DasMatcherResponseAdapter

"""
Fixtures for Response parsing
"""
lat1, lng1, lat2, lng2 = 10, 20, 15, 25
coord1 = GeoCoordinate(lat=lat1, lng=lng1)
coord2 = GeoCoordinate(lat=lat2, lng=lng2)
expected_geometry = Geometry([coord1, coord2])
geometry_das_translation = [{"lat": lat1, "lon": lng1}, {"lat": lat2, "lon": lng2}]
geometry_google_translation = "_c`|@_gayB_qo]_qo]"
expected_distance = 100
expected_duration = 50
expected_route = Route(
    distance=expected_distance, duration=expected_duration, geometry=expected_geometry
)
expected_geometry_index1 = Geometry([coord2, coord1, coord2, coord1])
geometry_index1_das_translation = [
    {"lat": lat2, "lon": lng2},
    {"lat": lat1, "lon": lng1},
    {"lat": lat2, "lon": lng2},
    {"lat": lat1, "lon": lng1},
]
geometry_index1_google_translation = "_upzA_yqwC~po]~po]_qo]_qo]~po]~po]"
expected_distance_index1 = 300
expected_duration_index1 = 150
expected_route_index1 = Route(
    distance=expected_distance_index1,
    duration=expected_duration_index1,
    geometry=expected_geometry_index1,
)

das_response = {
    "routes": [
        {
            "legs": [{"geometry": geometry_das_translation}],
            "totalDistance": expected_distance,
            "totalDuration": expected_duration,
        },
        {
            "legs": [{"geometry": geometry_index1_das_translation}],
            "totalDistance": expected_distance_index1,
            "totalDuration": expected_duration_index1,
        },
        {"legs": [{"geometry": []}]},  # empty geo
    ]
}

google_response = {
    "routes": [
        {
            "legs": [
                {
                    "distance": {"value": expected_distance},
                    "duration": {"value": expected_duration},
                }
            ],
            "overview_polyline": {"points": geometry_google_translation},
        },
        {
            "legs": [  # splitting into 3 legs for testing
                {
                    "distance": {"value": expected_distance_index1 / 3},
                    "duration": {"value": expected_duration_index1 / 3},
                },
                {
                    "distance": {"value": expected_distance_index1 / 3},
                    "duration": {"value": expected_duration_index1 / 3},
                },
                {
                    "distance": {"value": expected_distance_index1 / 3},
                    "duration": {"value": expected_duration_index1 / 3},
                },
            ],
            "overview_polyline": {"points": geometry_index1_google_translation},
        },
        {"legs": [{"geometry": []}]},  # empty geo
    ]
}

"""
Fixtures for Request serialization
"""
start_lat, start_lng, end_lat, end_lng = 10, 20, 30, 40
route_plan = RoutePlan(
    Waypoint(start_lat, start_lng),
    Waypoint(end_lat, end_lng),
    vehicle="CAR",
    strategy="FASTEST",
)

das_request_payload = {
    "locations": [
        {"lon": start_lng, "lat": start_lat},
        {"lon": end_lng, "lat": end_lat},
    ],
    "reportGeometry": True,
}

das_car_url = "https://routing.develop.otonomousmobility.com/car/v1/route"
das_car_traffic_url = (
    "https://routing.develop.otonomousmobility.com/car-traffic/v1/route"
)

google_key = "AIzaSyAKez1fnc-yOASRC3UeFOpSGispN1uuHjI"
google_car_url = (
    f"https://maps.googleapis.com/maps/api/directions/json?"
    f"origin={start_lat},{start_lng}&"
    f"destination={end_lat},{end_lng}&key={google_key}&units=metric"
)
google_car_url_multiple_waypoints = ""


@pytest.fixture()
def setup_das_router_environment(mocker):
    json_response_mock = Mock()
    response_mock = Mock(
        json=Mock(return_value=json_response_mock), elapsed=Mock(microseconds=100)
    )
    mocker.patch("requests.post", return_value=response_mock)
    route_mock = Mock()
    adapter_instance_mock = Mock(get_route=Mock(return_value=route_mock))
    adapter_mock = Mock(DasResponseAdapter, return_value=adapter_instance_mock)
    mocker.patch("das.routing.services.routing.DasResponseAdapter", adapter_mock)
    return {
        "json_response_mock": json_response_mock,
        "response_mock": response_mock,
        "route_mock": route_mock,
        "adapter_instance_mock": adapter_instance_mock,
        "adapter_mock": adapter_mock,
    }


@pytest.fixture()
def setup_google_router_environment(mocker):
    json_response_mock = Mock()
    response_mock = Mock(
        json=Mock(return_value=json_response_mock), elapsed=Mock(microseconds=100)
    )
    mocker.patch("requests.get", return_value=response_mock)
    route_mock = Mock()
    adapter_instance_mock = Mock(get_route=Mock(return_value=route_mock))
    adapter_mock = Mock(GoogleResponseAdapter, return_value=adapter_instance_mock)
    mocker.patch("das.routing.services.routing.GoogleResponseAdapter", adapter_mock)
    return {
        "json_response_mock": json_response_mock,
        "response_mock": response_mock,
        "route_mock": route_mock,
        "adapter_instance_mock": adapter_instance_mock,
        "adapter_mock": adapter_mock,
    }


@pytest.fixture()
def setup_calculate_route_environment():
    route_mock = Mock(Route, name="route_mock")
    router_instance_mock = Mock(
        calculate=Mock(return_value=route_mock, name="calculate_mock"),
        name="router_instance_mock",
    )
    router_mock = Mock(return_value=router_instance_mock, name="router_mock")
    router_mock.name = "provider"
    return {
        "route_mock": route_mock,
        "router_instance_mock": router_instance_mock,
        "router_mock": router_mock,
    }


@pytest.fixture()
def setup_calculate_competitive_environment():
    route_mock_provider_1 = Mock(name="route_mock_1")
    router_1_instance_mock = Mock(
        calculate=Mock(return_value=route_mock_provider_1, name="calculate_mock_1"),
        name="router_1_instance_mock",
    )
    router_1_mock = Mock(return_value=router_1_instance_mock, name="router_1_mock")
    router_1_mock.name = "provider1"
    route_mock_provider_2 = Mock(name="route_mock_2")
    router_2_instance_mock = Mock(
        calculate=Mock(return_value=route_mock_provider_2, name="calculate_mock_2"),
        name="router_2_instance_mock",
    )
    router_2_mock = Mock(return_value=router_2_instance_mock, name="router_2_mock")
    router_2_mock.name = "provider2"
    return [
        {
            "route_mock": route_mock_provider_1,
            "router_mock": router_1_mock,
            "router_instance_mock": router_1_instance_mock,
        },
        {
            "route_mock": route_mock_provider_2,
            "router_mock": router_2_mock,
            "router_instance_mock": router_2_instance_mock,
        },
    ]
