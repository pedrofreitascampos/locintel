from datetime import datetime
import os

from ratelimit import limits, sleep_and_retry
import requests

from das.routing.core.datamodel.geo import GeoCoordinate, Geometry
from das.routing.core.datamodel.routing import Route
from das.routing.core.datamodel.matching import MatchPlan

ROUTER_CALLS = 1200 if os.getenv("ROUTER_ENV") == "staging" else -1
ROUTER_PERIOD = 60 if os.getenv("ROUTER_ENV") == "staging" else -1


class AbstractMatcher(object):
    def __init__(self, host, adapter):
        self.host = host
        self.adapter = adapter
        self.last_response = None

    def calculate(self, *arg, **kwargs):
        raise NotImplementedError("Please implement subclass method")


class DasMatcher(AbstractMatcher):
    def __init__(
        self,
        endpoint="https://routing.develop.otonomousmobility.com/car/v1/match",
        user=None,
        password=None,
        headers=None,
        adapter=None,
    ):
        adapter = adapter or DasMatcherResponseAdapter
        super().__init__(endpoint, adapter)
        self.user = user
        self.password = password
        self.headers = {"Content-Type": "application/json"} or headers
        self.name = "das-matching"

    @sleep_and_retry
    @limits(calls=ROUTER_CALLS, period=ROUTER_PERIOD)  # allow 20req/s
    def calculate(self, match_plan: MatchPlan, **options):
        payload = self._generate_payload(match_plan, **options)
        url = self.host
        self.last_response = requests.post(
            url, json=payload, auth=(self.user, self.password), headers=self.headers
        )

        self.last_response.raise_for_status()
        return self.adapter(self.last_response.json()).get_route(
            metadata={
                "calc_time": self.last_response.elapsed.microseconds / 1e6,
                "date": datetime.now(),
            }
        )

    @staticmethod
    def _generate_payload(match_plan: MatchPlan, **kwargs):
        locations = []
        timestamps = []
        for point in match_plan.points:
            location = {"lat": point.lat, "lng": point.lng}

            for option in ["bearing", "radius"]:
                option_value = getattr(point, option)
                if option_value:
                    location.update({option: option_value})

            locations.append(location)

            if point.time:
                timestamps.append(point.time)

        payload = {"locations": locations}

        if timestamps and len(timestamps) == len(locations):
            payload.update({"timestamps": timestamps})
        elif len(timestamps) != len(locations):
            raise ValueError(
                f"Timestamps length ({len(timestamps)}) must be same as locations length {len(locations)}"
            )

        for k, v in kwargs.items():
            payload.update({k: v})

        return payload


class AbstractMatcherResponseAdapter(object):
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


class DasMatcherResponseAdapter(AbstractMatcherResponseAdapter):
    def __init__(self, response):
        super().__init__(response)

    def get_route(self, index=0, **kwargs):
        kwargs["metadata"].update(
            {
                "confidence": self.get_confidence(index),
                "max_snap_distance": self.get_max_snap_distance(),
                "failed_points": self.get_failed_points(),
                "raw": self.response,
            }
        )
        return Route(
            self.get_geometry(index),
            self.get_distance(index),
            self.get_duration(index),
            **kwargs,
        )

    def get_geometry(self, index=0):
        match = self.response["matchings"][index]
        match_geometry = []
        for leg in match["legs"]:
            match_geometry.extend(
                map(
                    lambda geo: GeoCoordinate(float(geo["lat"]), float(geo["lon"])),
                    leg["geometry"],
                )
            )
        return Geometry(match_geometry)

    def get_distance(self, index=0):
        match = self.response["matchings"][index]
        distance = 0
        for leg in match["legs"]:
            distance += leg["distance"]
        return distance

    def get_duration(self, index=0):
        match = self.response["matchings"][index]
        duration = 0
        for leg in match["legs"]:
            duration += leg["duration"]
        return duration

    def get_confidence(self, index=0):
        return self.response["matchings"][index]["confidence"]

    def get_max_snap_distance(self):
        return max(
            [
                tracepoint.get("snapDistance", 0)
                for tracepoint in self.response["tracepoints"]
            ]
        )

    def get_failed_points(self):
        return len(list(filter(lambda x: not x, self.response["tracepoints"])))


MATCHERS = {"das": DasMatcher}
