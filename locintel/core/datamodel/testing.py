import csv
from dataclasses import dataclass
import itertools
import numpy as np
from typing import Sequence

from locintel.core.datamodel.routing import Route, RoutePlan


@dataclass
class TestResult(object):
    def __init__(self, name, plan, routes, metrics=None):
        """
        Container class for a routing experiment, for several providers. It assumes 1 RoutePlan -> 1+ Route

        :param name: test name
        :param plan: original route plan, as locintel.core.datamodel.routing.RoutePlan object
        :param routes: route results as dict with providers as keys (e.g. routes={'mapbox':
        :param metrics: metrics associated to test, as dict, these are usually comparative between included routes,
                        for example, like route geometry comparison
        """
        self.name = name
        self.plan = plan
        self.routes = routes
        self.metrics = metrics or {}

    def __repr__(self):
        return f"TestResult(id={self.name},plan={self.plan},results={len(self.routes)})"

    def get_providers(self):
        return self.routes.keys()

    @classmethod
    def from_database_documents(cls, docs, test_name):
        """
        Create TestResult object from database documents (NOTE: docs must all belong to same test id)

        :param docs: list of jsons/database documents which are linked by the same test id
        :param test_name: test name, as string
        """
        if not docs:
            raise ValueError("No documents found")

        plan = RoutePlan.from_database_document(docs[0])
        routes = dict()
        for doc in docs:
            route_test_name = doc["routePlan"]["name"]
            provider = doc["provider"]["name"]
            if route_test_name != test_name:
                raise ValueError(
                    f"Found routes with different test ids in list: {route_test_name} vs {test_name}"
                )
            if provider in routes:
                routes[provider].append(Route.from_database_document(doc))
            else:
                routes[provider] = [Route.from_database_document(doc)]

        return cls(test_name, plan, routes)


@dataclass
class ExperimentResult(object):
    def __init__(self, tests: Sequence[TestResult]):
        """
        Container class for routing experiment

        :param tests: list of test results for the experiment, as TestResults object sequence
        """
        self.tests = tests

    def __iter__(self):
        yield from self.tests

    def __getitem__(self, item):
        return self.tests[item]

    def __repr__(self):
        return f"ExperimentResults(tests={len(self.tests)}, providers={self.get_providers()})"

    def get_plans(self):
        return [test.plan for test in self.tests]

    def get_providers(self):
        providers = list()
        for test in self.tests:
            for provider in test.get_providers():
                if provider not in providers:
                    providers.append(provider)
        return providers

    def get_metrics(self):
        metrics = list()
        for test in self.tests:
            for metric in test.metrics.keys():
                if metric not in metrics:
                    metrics.append(metric)
        return metrics

    def to_dataframe_consumable(self):
        return self._get_columns(), self._get_rows()

    def to_csv(self, filename):
        with open(filename, "w") as csvfile:
            result_writer = csv.writer(csvfile)
            result_writer.writerow(self._get_columns())
            rows = self._get_rows()
            for row in rows:
                result_writer.writerow(row)

    @classmethod
    def from_database_documents(cls, docs):
        """
        Create ExperimentResult object from database documents (NOTE: docs must all belong to same test id)

        :param docs: list of jsons/database documents which are linked by the same test id
        """
        test_results = list()
        for test, results in itertools.groupby(
            docs, key=lambda t: t["routePlan"]["name"]
        ):
            test_results.append(
                TestResult.from_database_documents(list(results), test_name=test)
            )
        return cls(tests=test_results)

    def _get_columns(self):
        providers = self.get_providers()
        metrics = self.get_metrics()
        return (
            ["name"]
            + [f"distance_{p}" for p in providers]
            + [f"duration_{p}" for p in providers]
            + [f"geometry_{p}" for p in providers]
            + [f"score_{m}" for m in metrics]
        )

    def _get_rows(self):
        metrics = self.get_metrics()
        rows = list()
        for test in self.tests:
            rows.append(
                [test.name]
                + self.__get_attrs(test, "distance")
                + self.__get_attrs(test, "duration")
                + [
                    geometry.to_polyline()
                    for geometry in self.__get_attrs(test, "geometry")
                ]
                + [test.metrics.get(metric, np.nan) for metric in metrics]
            )
        return rows

    def __get_attrs(self, test, attribute):
        return [
            getattr(test.routes[provider], attribute)
            for provider in self.get_providers()
            if provider in test.routes
        ]
