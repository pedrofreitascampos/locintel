from datetime import datetime

from unittest.mock import Mock, PropertyMock

expected_route_name = "mapbox-1"
expected_duration = 123
expected_distance = 126
expected_geometry = [
    [34.5, 12.11],
    [34.6, 12.12],
    [34.7, 12.13],
    [34.8, 12.14],
]  # lon, lat
expected_date = datetime(2019, 1, 1, 1, 0)
expected_calc_time = 0.12
expected_test_name = "mytaxi-berlin-1"
expected_test_name_2 = "mytaxi-berlin-2"
expected_route_plan = {
    "name": expected_test_name,
    "waypoints": [[1.5, 0.11], [-112.11, 34.5]],
}
expected_route_plan_mock = Mock()
expected_route_plan_name = PropertyMock(return_value=expected_route_plan["name"])
expected_route_plan_mock.name = expected_route_plan_name

expected_route_plan_2 = {
    "name": expected_test_name_2,
    "waypoints": [[3.5, 1.11], [112.11, 35.5]],
}
expected_provider = {
    "name": "mapbox",
    "api": "mapbox",
    "type": "router",
    "params": {"vehicle": "car", "strategy": "fastest", "endpoint": "routing.mapbox.car"},
}
expected_provider_google = {
    "name": "google",
    "api": "google",
    "type": "router",
    "options": {
        "vehicle": "driving",
        "strategy": "fastest",
        "endpoint": "routing.google",
    },
}
expected_test_run = {"name": "mytaxi-sanjose"}
expected_test_run_2 = {"name": "mytaxi-berlin"}

# expected metadata dict when building Route object from database document
expected_metadata = {
    "name": expected_route_name,
    "provider": expected_provider,
    "date": expected_date,
    "calc_time": expected_calc_time,
    "route_plan": expected_route_plan_mock,
    "test_run": expected_test_run,
}

route_mapbox = {
    "name": expected_route_name,
    "date": expected_date,
    "duration": expected_duration,
    "distance": expected_distance,
    "calcTime": expected_calc_time,
    "geometry": expected_geometry,
    "provider": expected_provider,
    "routePlan": expected_route_plan,
    "testRun": expected_test_run,
}

route_mapbox_older = {
    "name": "mapbox-1old",
    "date": datetime(2019, 1, 1, 0, 0),
    "duration": 129,
    "distance": 135,
    "calcTime": 0.22,
    "geometry": [[34.5, 12.11], [34.6, 12.12], [34.7, 12.15], [34.8, 12.14]],
    "provider": {"name": "Mapbox", "type": "routing", "url": "routing.mapbox.car"},
    "routePlan": expected_route_plan,
    "testRun": expected_test_run,
}

route_mapbox_2 = {
    "name": "mapbox-2",
    "date": datetime(2019, 1, 1, 1, 0),
    "duration": 123,
    "distance": 126,
    "calcTime": 1.2,
    "geometry": [[34.5, 12.11], [34.8, 12.14]],
    "provider": {"name": "Mapbox", "type": "routing", "url": "routing.mapbox.car"},
    "routePlan": expected_route_plan_2,
    "testRun": expected_test_run_2,
}

route_google = {
    "name": "google-1",
    "date": datetime(2019, 1, 1, 0, 0),
    "duration": 150,
    "distance": 160,
    "calcTime": 10.2,
    "provider": expected_provider_google,
    "routePlan": expected_route_plan,
    "geometry": [[34.5, 12.11], [34.6, 12.19], [34.7, 12.13], [34.8, 12.14]],
    "testRun": expected_test_run,
}

route_google_2 = {
    "name": "google-2",
    "date": datetime(2019, 1, 1, 0, 0),
    "duration": 300,
    "distance": 250,
    "calcTime": 100.0,
    "geometry": [[34.5, 12.11], [34.6, 12.19]],
    "provider": expected_provider_google,
    "routePlan": expected_route_plan_2,
    "testRun": expected_test_run_2,
}

route_mytaxi = {
    "name": "mytaxi-1",
    "date": datetime(2018, 1, 1, 0, 0),
    "duration": 200,
    "distance": 450,
    "calcTime": 0.001,
    "geometry": [[34.5, 12.11], [34.6, 12.12], [34.7, 12.13], [34.8, 12.14]],
    "provider": {"name": "mytaxi", "type": "trace", "url": ""},
    "routePlan": expected_route_plan,
    "testRun": expected_test_run_2,
}
