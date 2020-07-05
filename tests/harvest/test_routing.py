from copy import deepcopy
import multiprocessing
import requests

from locintel.core.datamodel.testing import TestResult, ExperimentResult
from locintel.services.routing import (
    MapboxRouter,
    GoogleRouter,
    calculate,
    calculate_competitive,
    run_experiment,
)

from unittest.mock import call

from tests.fixtures_routing import *


class TestMapboxResponseAdapter(object):
    def test_get_geometry(self):
        result = MapboxResponseAdapter(mapbox_response).get_geometry()

        assert isinstance(result, Geometry)
        assert result.coords == expected_geometry.coords

    def test_get_geometry_by_route_index(self):
        result = MapboxResponseAdapter(mapbox_response).get_geometry(index=1)

        assert isinstance(result, Geometry)
        assert result.coords == expected_geometry_index1.coords

    def test_get_geometry_raises_value_error_when_no_geometry_found(self):
        with pytest.raises(ValueError):
            MapboxResponseAdapter({}).get_geometry()

    def test_get_geometry_raises_value_error_when_geometry_empty(self):
        with pytest.raises(ValueError):
            MapboxResponseAdapter(mapbox_response).get_geometry(
                index=2
            )  # empty geo in fixtures with index=2

    def test_get_length(self):
        result = MapboxResponseAdapter(mapbox_response).get_distance()

        assert result == expected_distance

    def test_get_length_by_route_index(self):
        result = MapboxResponseAdapter(mapbox_response).get_distance(index=1)

        assert result == expected_distance_index1

    def test_get_length_raises_value_error_when_no_length_found(self):
        with pytest.raises(ValueError):
            MapboxResponseAdapter({}).get_distance()

    def test_get_duration(self):
        result = MapboxResponseAdapter(mapbox_response).get_duration()

        assert result == expected_duration

    def test_get_duration_by_route_index(self):
        result = MapboxResponseAdapter(mapbox_response).get_duration(index=1)

        assert result == expected_duration_index1

    def test_get_duration_raises_value_error_when_no_length_found(self):
        with pytest.raises(ValueError):
            MapboxResponseAdapter({}).get_duration()

    def test_get_route(self):
        result = MapboxResponseAdapter(mapbox_response).get_route()

        assert isinstance(result, Route)
        assert result == expected_route

    def test_get_route_by_route_index(self):
        result = MapboxResponseAdapter(mapbox_response).get_route(index=1)

        assert isinstance(result, Route)
        assert result == expected_route_index1


class TestGoogleResponseAdapter(object):
    def test_get_geometry(self, mocker):
        from_polyline_mock = Mock(return_value=expected_geometry)
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.from_polyline",
            side_effect=from_polyline_mock,
        )

        result = GoogleResponseAdapter(google_response).get_geometry()

        assert isinstance(result, Geometry)
        assert result.coords == expected_geometry.coords
        from_polyline_mock.assert_called_with(geometry_google_translation)

    def test_get_geometry_by_route_index(self, mocker):
        from_polyline_mock = Mock(return_value=expected_geometry_index1)
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.from_polyline",
            side_effect=from_polyline_mock,
        )
        result = GoogleResponseAdapter(google_response).get_geometry(index=1)

        assert isinstance(result, Geometry)
        assert result.coords == expected_geometry_index1.coords
        from_polyline_mock.assert_called_with(geometry_index1_google_translation)

    def test_get_geometry_raises_value_error_when_no_geometry_found(self):
        with pytest.raises(ValueError):
            GoogleResponseAdapter({}).get_geometry()

    def test_get_geometry_raises_value_error_when_geometry_empty(self):
        with pytest.raises(ValueError):
            GoogleResponseAdapter(google_response).get_geometry(
                index=2
            )  # empty geo in fixtures with index=2

    def test_get_length(self):
        result = GoogleResponseAdapter(google_response).get_distance()

        assert result == expected_distance

    def test_get_length_by_route_index(self):
        result = GoogleResponseAdapter(google_response).get_distance(index=1)

        assert result == expected_distance_index1

    def test_get_length_raises_value_error_when_length_not_found(self):
        with pytest.raises(ValueError):
            GoogleResponseAdapter({}).get_distance()

    def test_get_duration(self):
        result = GoogleResponseAdapter(google_response).get_duration()

        assert result == expected_duration

    def test_get_duration_by_route_index(self):
        result = GoogleResponseAdapter(google_response).get_duration(index=1)

        assert result == expected_duration_index1

    def test_get_duration_raises_value_error_when_duration_not_found(self):
        with pytest.raises(ValueError):
            GoogleResponseAdapter({}).get_duration()

    def test_get_route(self):
        result = GoogleResponseAdapter(google_response).get_route()

        assert isinstance(result, Route)
        assert result == expected_route

    def test_get_route_by_route_index(self):
        result = GoogleResponseAdapter(google_response).get_route(index=1)

        assert isinstance(result, Route)
        assert result == expected_route_index1


class TestMapboxRouter(object):
    def test_mapbox_router(self, setup_mapbox_router_environment):
        mocks = setup_mapbox_router_environment
        username = "username"
        password = "password"

        result = MapboxRouter(user=username, password=password).calculate(route_plan)

        assert result == mocks["route_mock"]
        requests.post.assert_called_with(
            mapbox_car_url, json=mapbox_request_payload, auth=(username, password)
        )
        mocks["response_mock"].json.assert_called()
        mocks["adapter_mock"].assert_called_with(mocks["json_response_mock"])
        mocks["adapter_instance_mock"].get_route.assert_called()

    def test_multiple_waypoints(self, setup_mapbox_router_environment):
        mocks = setup_mapbox_router_environment
        rp = deepcopy(route_plan)
        rp.intermediate_waypoints = [Waypoint(start_lat, end_lng)]
        payload = deepcopy(mapbox_request_payload)
        payload["locations"].insert(1, {"lon": end_lng, "lat": start_lat}),

        result = MapboxRouter().calculate(rp)

        assert result == mocks["route_mock"]
        requests.post.assert_called_with(mapbox_car_url, json=payload, auth=(None, None))
        mocks["response_mock"].json.assert_called()
        mocks["adapter_mock"].assert_called_with(mocks["json_response_mock"])
        mocks["adapter_instance_mock"].get_route.assert_called()

    def test_traffic(self, setup_mapbox_router_environment):
        mocks = setup_mapbox_router_environment

        result = MapboxRouter(traffic=True).calculate(route_plan)

        assert result == mocks["route_mock"]
        requests.post.assert_called_with(
            mapbox_car_traffic_url, json=mapbox_request_payload, auth=(None, None)
        )
        mocks["response_mock"].json.assert_called()
        mocks["adapter_mock"].assert_called_with(mocks["json_response_mock"])
        mocks["adapter_instance_mock"].get_route.assert_called()

    def test_kwargs(self, setup_mapbox_router_environment):
        mocks = setup_mapbox_router_environment

        new_payload = deepcopy(mapbox_request_payload)
        new_payload.update({"arg1": 1})

        result = MapboxRouter().calculate(route_plan, arg1=1)

        assert result == mocks["route_mock"]
        requests.post.assert_called_with(
            mapbox_car_url, json=new_payload, auth=(None, None)
        )
        mocks["response_mock"].json.assert_called()
        mocks["adapter_mock"].assert_called_with(mocks["json_response_mock"])
        mocks["adapter_instance_mock"].get_route.assert_called()

    def test_host(self, setup_mapbox_router_environment):
        mocks = setup_mapbox_router_environment
        hostname = "hostname/{vehicle_type}/v2"
        expected_url = hostname.format(vehicle_type="car")

        result = MapboxRouter(endpoint=hostname).calculate(route_plan)

        assert result == mocks["route_mock"]
        requests.post.assert_called_with(
            expected_url, json=mapbox_request_payload, auth=(None, None)
        )
        mocks["response_mock"].json.assert_called()
        mocks["adapter_mock"].assert_called_with(mocks["json_response_mock"])
        mocks["adapter_instance_mock"].get_route.assert_called()


class TestGoogleRouter(object):
    def test_google_router(self, setup_google_router_environment):
        mocks = setup_google_router_environment
        key = google_key

        result = GoogleRouter(key=key).calculate(route_plan)

        assert result == mocks["route_mock"]
        requests.get.assert_called_with(google_car_url)
        mocks["response_mock"].json.assert_called()
        mocks["adapter_mock"].assert_called_with(mocks["json_response_mock"])
        mocks["adapter_instance_mock"].get_route.assert_called()

    def test_multiple_waypoints_raises_not_implemented_error(self):
        rp = deepcopy(route_plan)
        rp.intermediate_waypoints = [Waypoint(start_lat, end_lng)]
        with pytest.raises(NotImplementedError):
            GoogleRouter().calculate(rp)

    def test_traffic(self):
        with pytest.raises(NotImplementedError):
            GoogleRouter(traffic=True)

    def test_kwargs(self, setup_google_router_environment):
        mocks = setup_google_router_environment
        kwargs = {"arg1": 1}

        result = GoogleRouter(**kwargs).calculate(route_plan)

        assert result == mocks["route_mock"]
        requests.get.assert_called_with(google_car_url + "&arg1=1")
        mocks["response_mock"].json.assert_called()
        mocks["adapter_mock"].assert_called_with(mocks["json_response_mock"])
        mocks["adapter_instance_mock"].get_route.assert_called()

    def test_host(self, setup_google_router_environment):
        mocks = setup_google_router_environment
        hostname = "google_hostname/google-car/v2/json?"
        url = deepcopy(google_car_url)
        url = url.replace(
            "https://maps.googleapis.com/maps/api/directions/json?", hostname
        )

        result = GoogleRouter(endpoint=hostname).calculate(route_plan)

        assert result == mocks["route_mock"]
        requests.get.assert_called_with(url)
        mocks["response_mock"].json.assert_called()
        mocks["adapter_mock"].assert_called_with(mocks["json_response_mock"])
        mocks["adapter_instance_mock"].get_route.assert_called()


class TestCalculate(object):
    def test_calculate(self, mocker, setup_calculate_route_environment):
        mocks = setup_calculate_route_environment
        d = {"provider": mocks["router_mock"]}
        mocker.patch.dict("locintel.services.routing.ROUTERS", d, clear=True)

        result = calculate(route_plan, mocks["router_mock"].name)

        assert isinstance(result, Route)
        assert result == mocks["route_mock"]
        mocks["router_mock"].assert_called_with()
        mocks["router_instance_mock"].calculate.assert_called_with(route_plan)

    def test_calculate_accepts_kwargs(self, mocker, setup_calculate_route_environment):
        mocks = setup_calculate_route_environment
        d = {"provider": mocks["router_mock"]}
        mocker.patch.dict("locintel.services.routing.ROUTERS", d, clear=True)
        kwargs = {"arg1": 1}

        result = calculate(route_plan, mocks["router_mock"].name, **kwargs)

        assert isinstance(result, Route)
        assert result == mocks["route_mock"]
        mocks["router_mock"].assert_called_with(arg1=1)
        mocks["router_instance_mock"].calculate.assert_called_with(route_plan)


class TestCalculateCompetitive(object):
    def test_calculate_competitive(
        self, mocker, setup_calculate_competitive_environment
    ):
        mocks = setup_calculate_competitive_environment
        router_1 = mocks[0]["router_mock"]
        router_2 = mocks[1]["router_mock"]
        d = {"provider1": router_1, "provider2": router_2}
        mocker.patch.dict("locintel.services.routing.ROUTERS", d, clear=True)
        routers = [router_1.name, router_2.name]

        result = calculate_competitive(route_plan, routers)

        assert isinstance(result, TestResult)
        assert result.name == str(route_plan)
        assert result.routes["provider1"] == mocks[0]["route_mock"]
        assert result.routes["provider2"] == mocks[1]["route_mock"]
        assert result.metrics == {}
        mocks[0]["router_instance_mock"].calculate.assert_called_with(route_plan)
        mocks[1]["router_instance_mock"].calculate.assert_called_with(route_plan)
        mocks[0][
            "route_mock"
        ].geometry.to_geojson.assert_not_called()  # make sure not writing to geojson by default

    def test_calculate_competitive_accepts_route_plan_identifier(
        self, mocker, setup_calculate_competitive_environment
    ):
        mocks = setup_calculate_competitive_environment
        router_1 = mocks[0]["router_mock"]
        router_2 = mocks[1]["router_mock"]
        d = {"provider1": router_1, "provider2": router_2}
        mocker.patch.dict("locintel.services.routing.ROUTERS", d, clear=True)
        ROUTERS = [mock["router_mock"].name for mock in mocks]
        rp = deepcopy(route_plan)
        rp.name = "name"

        result = calculate_competitive(rp, ROUTERS)

        assert isinstance(result, TestResult)
        assert result.name == rp.name
        assert result.routes["provider1"] == mocks[0]["route_mock"]
        assert result.routes["provider2"] == mocks[1]["route_mock"]
        assert result.metrics == {}
        mocks[0]["router_instance_mock"].calculate.assert_called_with(rp)
        mocks[1]["router_instance_mock"].calculate.assert_called_with(rp)

    def test_calculate_competitive_with_comparators(
        self, mocker, setup_calculate_competitive_environment
    ):
        mocks = setup_calculate_competitive_environment
        score1, score2 = 10, 20
        comparator1 = Mock(return_value=score1)
        comparator1.name = "comparator1"
        comparator2 = Mock(return_value=score2)
        comparator2.name = "comparator2"
        router_1 = mocks[0]["router_mock"]
        router_2 = mocks[1]["router_mock"]
        d = {"provider1": router_1, "provider2": router_2}
        mocker.patch.dict("locintel.services.routing.ROUTERS", d, clear=True)
        ROUTERS = [mock["router_mock"].name for mock in mocks]
        expected_metrics = {
            f"comparator1_{ROUTERS[0]}_vs_{ROUTERS[1]}": score1,
            f"comparator2_{ROUTERS[0]}_vs_{ROUTERS[1]}": score2,
        }

        result = calculate_competitive(
            route_plan, ROUTERS, comparators=[comparator1, comparator2]
        )

        assert isinstance(result, TestResult)
        assert result.name == str(route_plan)
        assert result.routes["provider1"] == mocks[0]["route_mock"]
        assert result.routes["provider2"] == mocks[1]["route_mock"]
        assert result.metrics == expected_metrics
        mocks[0]["router_instance_mock"].calculate.assert_called_with(route_plan)
        mocks[1]["router_instance_mock"].calculate.assert_called_with(route_plan)
        comparator1.assert_called_with(
            mocks[0]["route_mock"].geometry, mocks[1]["route_mock"].geometry
        )
        comparator2.assert_called_with(
            mocks[0]["route_mock"].geometry, mocks[1]["route_mock"].geometry
        )

    def test_calculate_competitive_more_than_two_ROUTERS_pairwise_scores(
        self, mocker, setup_calculate_competitive_environment
    ):
        mocks = setup_calculate_competitive_environment

        route_mock_provider_3 = Mock(metadata={"provider": {"name": "provider3"}})
        router_3_instance_mock = Mock(
            calculate=Mock(return_value=route_mock_provider_3)
        )
        router_3_mock = Mock(return_value=router_3_instance_mock)
        router_3_mock.name = "provider3"
        mocks.append(
            {
                "router_mock": router_3_mock,
                "route_mock": route_mock_provider_3,
                "router_instance_mock": router_3_instance_mock,
            }
        )
        score1_1vs2, score2_1vs2 = 10, 20  # Scores of router 1 vs 2
        score1_1vs3, score2_1vs3 = 10, 20  # Scores of router 1 vs 3
        score1_2vs3, score2_2vs3 = 10, 20  # Scores of router 2 vs 3
        comparator1 = Mock(side_effect=[score1_1vs2, score1_1vs3, score1_2vs3])
        comparator1.name = "comparator1"
        comparator2 = Mock(side_effect=[score2_1vs2, score2_1vs3, score2_2vs3])
        comparator2.name = "comparator2"
        router_1 = mocks[0]["router_mock"]
        router_2 = mocks[1]["router_mock"]
        router_3 = mocks[2]["router_mock"]
        d = {"provider1": router_1, "provider2": router_2, "provider3": router_3}
        mocker.patch.dict("locintel.services.routing.ROUTERS", d, clear=True)
        ROUTERS = [mock["router_mock"].name for mock in mocks]
        expected_metrics = {
            f"comparator1_{ROUTERS[0]}_vs_{ROUTERS[1]}": score1_1vs2,
            f"comparator2_{ROUTERS[0]}_vs_{ROUTERS[1]}": score2_1vs2,
            f"comparator1_{ROUTERS[0]}_vs_{ROUTERS[2]}": score1_1vs3,
            f"comparator2_{ROUTERS[0]}_vs_{ROUTERS[2]}": score2_1vs3,
            f"comparator1_{ROUTERS[1]}_vs_{ROUTERS[2]}": score1_2vs3,
            f"comparator2_{ROUTERS[1]}_vs_{ROUTERS[2]}": score2_2vs3,
        }
        comparator1_calls = [
            call(mocks[0]["route_mock"].geometry, mocks[1]["route_mock"].geometry),
            call(mocks[0]["route_mock"].geometry, mocks[2]["route_mock"].geometry),
            call(mocks[1]["route_mock"].geometry, mocks[2]["route_mock"].geometry),
        ]
        comparator2_calls = [
            call(mocks[0]["route_mock"].geometry, mocks[1]["route_mock"].geometry),
            call(mocks[0]["route_mock"].geometry, mocks[2]["route_mock"].geometry),
            call(mocks[1]["route_mock"].geometry, mocks[2]["route_mock"].geometry),
        ]

        result = calculate_competitive(
            route_plan, ROUTERS, comparators=[comparator1, comparator2]
        )

        assert isinstance(result, TestResult)
        assert result.name == str(route_plan)
        assert result.routes["provider1"] == mocks[0]["route_mock"]
        assert result.routes["provider2"] == mocks[1]["route_mock"]
        assert result.routes["provider3"] == mocks[2]["route_mock"]
        assert result.metrics == expected_metrics
        mocks[0]["router_instance_mock"].calculate.assert_called_with(route_plan)
        mocks[1]["router_instance_mock"].calculate.assert_called_with(route_plan)
        mocks[2]["router_instance_mock"].calculate.assert_called_with(route_plan)
        comparator1.assert_has_calls(comparator1_calls)
        comparator2.assert_has_calls(comparator2_calls)

    def test_calculate_test_write_to_geojson(
        self, mocker, setup_calculate_competitive_environment
    ):
        mocks = setup_calculate_competitive_environment
        mocker.patch("locintel.core.datamodel.geo.Geometry.to_geojson")
        router_1 = mocks[0]["router_mock"]
        router_2 = mocks[1]["router_mock"]
        d = {"provider1": router_1, "provider2": router_2}
        mocker.patch.dict("locintel.services.routing.ROUTERS", d, clear=True)
        ROUTERS = [mock["router_mock"].name for mock in mocks]
        output_dir = "output"
        rp = deepcopy(route_plan)
        rp.name = "name"
        expected_filename_provider_1 = f"{output_dir}/{rp.name}_{ROUTERS[0]}.json"
        expected_filename_provider_2 = f"{output_dir}/{rp.name}_{ROUTERS[1]}.json"

        result = calculate_competitive(rp, ROUTERS, write_geojson=output_dir)

        assert isinstance(result, TestResult)
        assert result.name == rp.name
        assert result.routes["provider1"] == mocks[0]["route_mock"]
        assert result.routes["provider2"] == mocks[1]["route_mock"]
        assert result.metrics == {}
        mocks[0]["router_instance_mock"].calculate.assert_called_with(route_plan)
        mocks[1]["router_instance_mock"].calculate.assert_called_with(route_plan)
        mocks[0]["route_mock"].geometry.to_geojson.assert_called_with(
            write_to=expected_filename_provider_1
        )
        mocks[1]["route_mock"].geometry.to_geojson.assert_called_with(
            write_to=expected_filename_provider_2
        )


class TestRunExperiment(object):
    def test_run_experiment(self, mocker, setup_calculate_competitive_environment):
        mocks = setup_calculate_competitive_environment
        test_result_1, test_result_2 = Mock(), Mock()
        pool = Mock(imap=Mock(return_value=[test_result_1, test_result_2]))
        mocker.patch("multiprocessing.Pool", return_value=pool)
        rp1 = route_plan
        rp2 = deepcopy(route_plan)
        rp2.end.lat = 11
        route_plans = [rp1, rp2]
        ROUTERS = [mock["router_mock"].name for mock in mocks]
        jobs = 7
        expected_result = ExperimentResult([test_result_1, test_result_2])

        result = run_experiment(route_plans, ROUTERS, jobs=jobs)

        assert result == expected_result
        multiprocessing.Pool.assert_called_with(jobs)
        #  TODO: mock functools.partial and test accepts comparators and write_geojson
