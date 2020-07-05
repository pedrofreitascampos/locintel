from datetime import datetime
import functools
import itertools
import multiprocessing
import requests

from das.routing.core.datamodel.geo import Geometry
from das.routing.core.datamodel.routing import Route
from das.routing.core.datamodel.testing import TestResult, ExperimentResult


class AbstractRouter(object):
    def __init__(self, endpoint, adapter):
        self.endpoint = endpoint
        self.adapter = adapter
        self.last_response = None

    def calculate(self, *arg, **kwargs):
        raise NotImplementedError("Please implement subclass method")


class DasRouter(AbstractRouter):
    def __init__(
        self,
        endpoint="https://routing.develop.otonomousmobility.com/{vehicle_type}/v1/route",
        user=None,
        password=None,
        traffic=False,
        adapter=None,
    ):
        adapter = adapter or DasResponseAdapter
        super().__init__(endpoint, adapter)
        self.user = user
        self.password = password
        self.traffic = traffic
        self.name = "das-routing-traffic" if traffic else "das-routing"

    def calculate(self, route_plan, **kwargs):
        payload = DasRouter._generate_payload(route_plan, **kwargs)
        url = self.endpoint.format(
            vehicle_type=route_plan.vehicle.lower()
            + ("-traffic" if self.traffic else "")
        )
        self.last_response = requests.post(
            url, json=payload, auth=(self.user, self.password)
        )

        self.last_response.raise_for_status()
        return self.adapter(self.last_response.json()).get_route(
            metadata={
                "calc_time": self.last_response.elapsed.microseconds / 1e6,
                "date": datetime.now(),
            }
        )

    @staticmethod
    def _generate_payload(route_plan, **kwargs):
        payload = {
            "locations": [
                {"lon": w.lng, "lat": w.lat} for w in route_plan.get_waypoints()
            ],
            "reportGeometry": True,
        }

        for k, v in kwargs.items():
            payload.update({k: v})

        return payload


class GoogleRouter(AbstractRouter):
    GOOGLE_OPTIONS_TRANSLATOR = {
        "vehicle": {"CAR": "driving", "PEDESTRIAN": "walking", "BIKE": "bicycling"}
    }

    def __init__(
        self,
        endpoint="https://maps.googleapis.com/maps/api/directions/json?",
        key="AIzaSyAKez1fnc-yOASRC3UeFOpSGispN1uuHjI",
        adapter=None,
        **kwargs,
    ):
        adapter = adapter or GoogleResponseAdapter
        super().__init__(endpoint, adapter)
        self.key = key
        self.options = {"units": "metric"}
        self.options.update(**kwargs)
        if "traffic" in self.options:
            raise NotImplementedError
        self.name = "google"

    def calculate(self, route_plan):
        if route_plan.intermediate_waypoints:
            raise NotImplementedError

        origin = f"{route_plan.start.lat},{route_plan.start.lng}"
        destination = f"{route_plan.end.lat},{route_plan.end.lng}"

        url = f"{self.endpoint}origin={origin}&destination={destination}&key={self.key}"
        for k, v in self.options.items():
            url += f"&{k}={v}"

        self.last_response = requests.get(url)
        return self.adapter(self.last_response.json()).get_route(
            metadata={
                "calc_time": self.last_response.elapsed.microseconds / 1e6,
                "date": datetime.now(),
            }
        )


class AbstractResponseAdapter(object):
    def __init__(self, response):
        self.response = response

    def get_geometry(self, index=0):
        raise NotImplementedError("Please implement subclass method")

    def get_distance(self, index=0):
        raise NotImplementedError("Please implement subclass method")

    def get_duration(self, index=0):
        raise NotImplementedError("Please implement subclass method")

    def get_route(self, index=0, **kwargs):
        raise NotImplementedError("Please implement subclass method")


class DasResponseAdapter(AbstractResponseAdapter):
    def __init__(self, response):
        super().__init__(response)

    def get_geometry(self, index=0):
        geometry = list()
        try:
            for leg in self.response["routes"][index]["legs"]:
                geometry.extend(leg["geometry"])
        except KeyError:
            raise ValueError(
                'Could not find geometry field in response (["routes"][index]["legs"][index]["geometry"])'
            )
        return Geometry.from_lat_lon_dicts(geometry)

    def get_distance(self, index=0):
        try:
            return self.response["routes"][index]["totalDistance"]
        except KeyError:
            raise ValueError(
                'Could not find distance field in response (["routes"][index]["totalDistance"])'
            )

    def get_duration(self, index=0):
        try:
            return self.response["routes"][index]["totalDuration"]
        except KeyError:
            raise ValueError(
                'Could not find distance field in response (["routes"][index]["totalDuration"])'
            )

    def get_route(self, index=0, **kwargs):
        return Route(
            geometry=self.get_geometry(index=index),
            distance=self.get_distance(index=index),
            duration=self.get_duration(index=index),
            **kwargs,
        )


class GoogleResponseAdapter(AbstractResponseAdapter):
    def __init__(self, response):
        super().__init__(response)

    def get_geometry(self, index=0):
        try:
            return Geometry.from_polyline(
                self.response["routes"][index]["overview_polyline"]["points"]
            )
        except KeyError:
            raise ValueError(
                "Could not find geometry field in response "
                '(["routes"][index]["overview_polyline"]["points"]'
            )

    def get_distance(self, index=0):
        distance = 0
        try:
            for leg in self.response["routes"][index]["legs"]:
                distance += leg["distance"]["value"]
        except KeyError:
            raise ValueError(
                "Could not find distance field in response "
                '(["routes"][index]["legs"][index]["distance"]["value"])'
            )
        return distance

    def get_duration(self, index=0):
        duration = 0
        try:
            for leg in self.response["routes"][index]["legs"]:
                duration += leg["duration"]["value"]
        except KeyError:
            raise ValueError(
                "Could not find duration field in response "
                '(["routes"][index]["legs"][index]["duration"]["value"])'
            )
        return duration

    def get_route(self, index=0, **kwargs):
        return Route(
            geometry=self.get_geometry(index=index),
            distance=self.get_distance(index=index),
            duration=self.get_duration(index=index),
            **kwargs,
        )


# FROM HERE ONWARDS LIES SYNTACTIC SUGAR
ROUTERS = {
    "das": DasRouter,
    "google": GoogleRouter,
    "das-traffic": functools.partial(DasRouter, traffic=True),
}


def calculate(route_plan, provider, **kwargs):
    return ROUTERS[provider](**kwargs).calculate(route_plan)


def calculate_competitive(route_plan, providers, comparators=None, write_geojson=None):
    """
    Calculates test, in which multiple providers are assumed for a given RoutePlan/test
    """
    results = dict()
    for provider in providers:
        router = ROUTERS[provider]()
        route = router.calculate(route_plan)
        results[provider] = route

        if write_geojson:
            try:
                route.geometry.to_geojson(
                    write_to=f"{write_geojson}/{route_plan.name}_{provider}.json"
                )
            except AttributeError:
                raise AttributeError(
                    "No name found on RoutePlan, must specify name to write to geojson"
                )

    comparators = comparators or []
    metrics = dict()
    for comparator in comparators:
        score_name = getattr(comparator, "name", str(comparator))
        for pair in itertools.combinations(providers, 2):
            provider1, provider2 = pair[0], pair[1]
            score = comparator(results[provider1].geometry, results[provider2].geometry)
            metrics[score_name + f"_{provider1}_vs_{provider2}"] = score

    return TestResult(
        getattr(route_plan, "name", str(route_plan)), route_plan, results, metrics
    )


def run_experiment(
    providers, route_plans, jobs=7, comparators=None, write_geojson=None
):
    """
    Calculates experiments, in which multiple providers are assumed for multiples RoutePlans.

    Uses multiprocessing to parallelize requests and improve performance
    """
    p = multiprocessing.Pool(jobs)

    calculate_providers = functools.partial(
        calculate_competitive,
        providers=providers,
        comparators=comparators,
        write_geojson=write_geojson,
    )

    return ExperimentResult(
        [test_result for test_result in p.imap(calculate_providers, route_plans)]
    )
