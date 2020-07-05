from das.routing.core.datamodel.testing import *
from tests.fixtures.testing import *

import pytest
from unittest.mock import Mock, mock_open, patch, call


@pytest.fixture()
def mock_routes():
    return {
        expected_provider["name"]: Mock(Route),
        expected_provider_google["name"]: Mock(Route),
    }


class TestTestResult(object):
    def test_test_result(self, mock_routes):
        name = "name"
        plan = Mock()
        routes = mock_routes
        metrics = {"metric1": 1, "metric2": 2}

        result = TestResult(name=name, plan=plan, routes=routes, metrics=metrics)

        assert result.plan == plan
        assert result.name == name
        assert result.routes == routes
        assert result.metrics == metrics

    def test_get_providers(self, mock_routes):
        name = "name"
        routes = mock_routes
        provider_1, provider_2 = routes.keys()
        plan = Mock()
        metrics = {"metric1": 1, "metric2": 2}
        tests = TestResult(name=name, plan=plan, routes=routes, metrics=metrics)

        result = tests.get_providers()

        assert sorted(result) == [provider_1, provider_2]

    def test_from_database_documents(self, mocker, mock_routes):
        expected_routes = mock_routes
        route_plan_from_database_document = Mock(return_value=expected_route_plan_mock)
        route_from_database_document = Mock(side_effect=expected_routes)
        mocker.patch(
            "das.routing.core.datamodel.routing.RoutePlan.from_database_document",
            route_plan_from_database_document,
        )
        mocker.patch(
            "das.routing.core.datamodel.routing.Route.from_database_document",
            route_from_database_document,
        )
        routes = [route_das, route_google]  # both fixtures share same test id

        result = TestResult.from_database_documents(routes, expected_test_name)

        assert isinstance(result, TestResult)
        assert result.plan == expected_route_plan_mock
        assert result.name == expected_test_name
        assert result.routes.keys() == expected_routes.keys()
        route_plan_from_database_document.assert_called_with(route_das)
        route_from_database_document.assert_has_calls(
            [call(route_das), call(route_google)]
        )

    def test_from_database_documents_empty_docs_raises_value_error(self):
        with pytest.raises(ValueError):
            TestResult.from_database_documents([], expected_test_name)

    def test_from_database_documents_include_tests_with_different_ids_raise_value_error(
        self, mocker
    ):
        route_plan = Mock()
        from_database_document = Mock(return_value=route_plan)
        mocker.patch(
            "das.routing.core.datamodel.routing.RoutePlan.from_database_document",
            from_database_document,
        )
        routes = [route_das, route_das_2]  # different test ids

        with pytest.raises(ValueError):
            TestResult.from_database_documents(routes, expected_test_name)


class TestExperimentResult(object):
    def test_experiment_result(self):
        tests = [Mock(TestResult), Mock(TestResult)]

        result = ExperimentResult(tests=tests)

        assert result.tests == tests

    def test_iterator_returns_test_results(self):
        tests = [Mock(TestResult), Mock(TestResult)]

        result = ExperimentResult(tests=tests)

        assert list(result) == tests

    def test_getitem_returns_test_item(self):
        tests = [Mock(TestResult), Mock(TestResult)]

        result = ExperimentResult(tests=tests)

        assert result[0] == tests[0]

    def test_get_plans(self):
        plan_1, plan_2 = Mock(), Mock()
        test_1, test_2 = Mock(TestResult, plan=plan_1), Mock(TestResult, plan=plan_2)
        tests = [test_1, test_2]

        result = ExperimentResult(tests=tests).get_plans()

        assert result == [plan_1, plan_2]

    def test_get_providers(self):
        providers = ["provider_1", "provider_2"]
        test_1 = Mock(
            TestResult,
            routes=[Mock(Route), Mock(Route)],
            get_providers=Mock(return_value=providers),
        )
        test_2 = Mock(
            TestResult,
            routes=[Mock(Route), Mock(Route)],
            get_providers=Mock(return_value=providers),
        )
        tests = [test_1, test_2]
        experiment_results = ExperimentResult(tests=tests)

        result = experiment_results.get_providers()

        assert result == providers

    def test_get_providers_returns_union_of_all_providers_in_tests(self):
        #  If some tests have some providers and other tests others, we are interested in the union
        providers_1 = ["provider_1", "provider_2"]
        providers_2 = ["provider_3", "provider_2"]
        test_1 = Mock(
            TestResult,
            routes=[Mock(Route), Mock(Route)],
            get_providers=Mock(return_value=providers_1),
        )
        test_2 = Mock(
            TestResult,
            routes=[Mock(Route), Mock(Route)],
            get_providers=Mock(return_value=providers_2),
        )
        tests = [test_1, test_2]
        experiment_results = ExperimentResult(tests=tests)

        result = experiment_results.get_providers()

        assert result == ["provider_1", "provider_2", "provider_3"]

    def test_get_metrics(self):
        metrics = {"metric_1": 1, "metric_2": 2}
        test_1 = Mock(TestResult, routes=[Mock(Route), Mock(Route)], metrics=metrics)
        test_2 = Mock(TestResult, routes=[Mock(Route), Mock(Route)], metrics=metrics)
        tests = [test_1, test_2]
        experiment_results = ExperimentResult(tests=tests)

        result = experiment_results.get_metrics()

        assert sorted(result) == sorted(metrics.keys())

    def test_get_metrics_returns_union_of_all_metrics_in_tests(self):
        metrics_1 = {"metric_1": 1, "metric_2": 2}
        metrics_2 = {"metric_3": 10, "metric_1": 20}
        test_1 = Mock(TestResult, metrics=metrics_1)
        test_2 = Mock(TestResult, metrics=metrics_2)
        tests = [test_1, test_2]
        experiment_results = ExperimentResult(tests=tests)

        result = experiment_results.get_metrics()

        assert sorted(result) == ["metric_1", "metric_2", "metric_3"]

    def test_write_to_csv(self, mocker):
        metrics_1 = {"hausdorff": 100, "pmr": 0.8}
        metrics_2 = {"hausdorff": 7000, "pmr": 0.1, "cir": 0.8}
        metrics = ["hausdorff", "pmr", "cir"]
        providers = ["provider_1", "provider_2"]
        route_1_provider_1 = Mock(
            distance=10,
            duration=20,
            geometry=Mock(to_polyline=lambda: "abc"),
            metadata={"provider": {"name": providers[0]}},
        )
        route_1_provider_2 = Mock(
            distance=12,
            duration=25,
            geometry=Mock(to_polyline=lambda: "abd"),
            metadata={"provider": {"name": providers[1]}},
        )
        route_2_provider_1 = Mock(
            distance=20,
            duration=30,
            geometry=Mock(to_polyline=lambda: "zxy"),
            metadata={"provider": {"name": providers[0]}},
        )
        route_2_provider_2 = Mock(
            distance=15,
            duration=35,
            geometry=Mock(to_polyline=lambda: "zxv"),
            metadata={"provider": {"name": providers[1]}},
        )
        test_1 = Mock(
            TestResult,
            routes={providers[0]: route_1_provider_1, providers[1]: route_1_provider_2},
            metrics=metrics_1,
        )
        test_1.name = "test_1"
        test_2 = Mock(
            TestResult,
            routes={providers[0]: route_2_provider_1, providers[1]: route_2_provider_2},
            metrics=metrics_2,
        )
        test_2.name = "test_2"
        tests = [test_1, test_2]
        filename = "filename"
        mocker.patch(
            "das.routing.core.datamodel.testing.ExperimentResult.get_providers",
            return_value=providers,
        )
        mocker.patch(
            "das.routing.core.datamodel.testing.ExperimentResult.get_metrics",
            return_value=metrics,
        )
        writer_mock = Mock(writerow=Mock())
        mocker.patch("csv.writer", return_value=writer_mock)
        m = mock_open()
        experiment_results = ExperimentResult(tests=tests)

        with patch("das.routing.core.datamodel.testing.open", m, create=True):
            experiment_results.to_csv(filename)

        m.assert_called_with(filename, "w")
        header = call(
            [
                "name",
                "distance_provider_1",
                "distance_provider_2",
                "duration_provider_1",
                "duration_provider_2",
                "geometry_provider_1",
                "geometry_provider_2",
                "score_hausdorff",
                "score_pmr",
                "score_cir",
            ]
        )
        row_test_1 = call(["test_1", 10, 12, 20, 25, "abc", "abd", 100, 0.8, np.nan])
        row_test_2 = call(["test_2", 20, 15, 30, 35, "zxy", "zxv", 7000, 0.1, 0.8])
        writer_mock.writerow.assert_has_calls([header, row_test_1, row_test_2])

    def test_write_to_dataframe_consumable(self, mocker):
        cols_mock = Mock()
        rows_mock = Mock()
        mocker.patch(
            "das.routing.core.datamodel.testing.ExperimentResult._get_columns",
            return_value=cols_mock,
        )
        mocker.patch(
            "das.routing.core.datamodel.testing.ExperimentResult._get_rows",
            return_value=rows_mock,
        )

        experiment = ExperimentResult(tests=[Mock(), Mock()])
        result = experiment.to_dataframe_consumable()

        assert result == (cols_mock, rows_mock)
        experiment._get_columns.assert_called()
        experiment._get_rows.assert_called()

    def test_from_database_documents(self, mocker):
        expected_test_results = [Mock(), Mock()]
        test_result_from_database_document = Mock(side_effect=expected_test_results)
        mocker.patch(
            "das.routing.core.datamodel.testing.TestResult.from_database_documents",
            test_result_from_database_document,
        )
        routes_test_1 = [route_das, route_google]  # routes with test id 1
        routes_test_2 = [route_das_2, route_google_2]  # routes with test id 2
        routes = routes_test_1 + routes_test_2  # document has routes from both tests

        result = ExperimentResult.from_database_documents(routes)

        assert isinstance(result, ExperimentResult)
        assert result.tests == expected_test_results
        call_1 = call(routes_test_1, test_name=expected_test_name)
        call_2 = call(routes_test_2, test_name=expected_test_name_2)
        test_result_from_database_document.assert_has_calls([call_1, call_2])
